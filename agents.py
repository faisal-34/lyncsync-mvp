import json
import logging
import os
import re
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from connectors import ConnectorHub

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - exercised when dependencies are not installed
    genai = None
    types = None


logger = logging.getLogger(__name__)


class ParsedIntent(BaseModel):
    task: str = Field(..., description="Primary action requested by the user.")
    target_platform: str = Field(
        ..., description="Primary platform or business domain for the action."
    )
    data: Dict[str, Any] = Field(
        default_factory=dict, description="Structured entities extracted from the request."
    )


class ExecutionStep(BaseModel):
    tool: Literal["update_crm", "notify_team"]
    payload: Dict[str, Any]


class IntentExecutionResult(BaseModel):
    parsed_intent: ParsedIntent
    plan: List[ExecutionStep]
    results: List[Dict[str, Any]]


class GeminiIntentAgent:
    """Gemini-backed intent parser that uses function calling to enforce structure."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.client = client or self._build_client()

    def _build_client(self) -> Any | None:
        if genai is None:
            return None

        if not self.api_key:
            return None

        return genai.Client(api_key=self.api_key)

    def _extract_function_call(self, response: Any) -> Any:
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", []) or []:
                function_call = getattr(part, "function_call", None)
                if function_call:
                    return function_call

        raise ValueError("Gemini did not return a function call for the provided intent.")

    def _extract_client_name(self, user_intent: str, data: Dict[str, Any]) -> str | None:
        candidate = data.get("client_name") or data.get("name") or data.get("client")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()

        match = re.search(
            r"onboard(?:ing)?\s+(?:a\s+)?new client named\s+(.+)$",
            user_intent.strip(),
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1).strip().rstrip(".")

        return None

    def _normalize_parsed_intent(
        self, parsed: ParsedIntent, user_intent: str
    ) -> ParsedIntent:
        normalized_task = parsed.task.strip().lower().replace(" ", "_")
        normalized_platform = parsed.target_platform.strip() or "unmapped"
        normalized_data = dict(parsed.data)
        normalized_data.setdefault("raw_intent", user_intent)

        client_name = self._extract_client_name(user_intent, normalized_data)
        if client_name:
            normalized_data["client_name"] = client_name

        if normalized_task in {"onboard_client", "onboard_new_client"} and client_name:
            normalized_data.setdefault("requested_action", "onboard_new_client")
            normalized_task = "onboard_client"
            normalized_platform = "crm_and_team_ops"

        return ParsedIntent(
            task=normalized_task or "unknown",
            target_platform=normalized_platform,
            data=normalized_data,
        )

    def parse_intent(self, user_intent: str) -> ParsedIntent:
        logger.info("Parsing user intent: %s", user_intent)

        if self.client is None or types is None:
            raise RuntimeError(
                "Gemini client is not configured. Install `google-genai` and set "
                "the GEMINI_API_KEY environment variable."
            )

        parse_intent_declaration = types.FunctionDeclaration(
            name="parse_intent",
            description=(
                "Parse a natural-language orchestration request into the LyncSync schema."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": (
                            "Normalized task name such as onboard_client, update_user, "
                            "notify_team, or unknown."
                        ),
                    },
                    "target_platform": {
                        "type": "string",
                        "description": (
                            "Primary target platform or operational domain affected by the task."
                        ),
                    },
                    "data": {
                        "type": "object",
                        "description": (
                            "Structured entities extracted from the prompt, such as "
                            "client_name, system names, or message text."
                        ),
                    },
                },
                "required": ["task", "target_platform", "data"],
            },
        )
        tools = [types.Tool(function_declarations=[parse_intent_declaration])]
        tool_config = types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode="ANY",
                allowed_function_names=["parse_intent"],
            )
        )
        config = types.GenerateContentConfig(
            tools=tools,
            tool_config=tool_config,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_intent,
            config=config,
        )
        function_call = self._extract_function_call(response)

        if function_call.name != "parse_intent":
            raise ValueError(
                f"Unexpected Gemini function returned: {function_call.name}"
            )

        parsed = ParsedIntent.model_validate(function_call.args)
        parsed = self._normalize_parsed_intent(parsed, user_intent)
        logger.info("Parsed Gemini intent: %s", parsed.model_dump_json())
        return parsed

    def build_execution_plan(self, parsed_intent: ParsedIntent) -> List[ExecutionStep]:
        logger.info("Building execution plan for task: %s", parsed_intent.task)

        if parsed_intent.task == "onboard_client":
            client_name = parsed_intent.data.get("client_name")
            if not isinstance(client_name, str) or not client_name.strip():
                logger.warning("Parsed onboarding intent is missing client_name.")
                return []
            return [
                ExecutionStep(tool="update_crm", payload=parsed_intent.data),
                ExecutionStep(
                    tool="notify_team",
                    payload={
                        "message": f"New client onboarding started for {client_name}."
                    },
                ),
            ]

        return []


class OrchestratorService:
    def __init__(
        self,
        connector_hub: ConnectorHub | None = None,
        agent: GeminiIntentAgent | None = None,
    ) -> None:
        self.agent = agent or GeminiIntentAgent()
        self.connector_hub = connector_hub or ConnectorHub()

    def handle_intent(self, user_intent: str) -> IntentExecutionResult:
        parsed_intent = self.agent.parse_intent(user_intent)
        plan = self.agent.build_execution_plan(parsed_intent)
        results: List[Dict[str, Any]] = []

        if not plan:
            logger.info("No executable plan generated for intent: %s", user_intent)
            return IntentExecutionResult(
                parsed_intent=parsed_intent,
                plan=[],
                results=[
                    {
                        "status": "noop",
                        "message": "Intent parsed but no workflow is mapped for execution.",
                    }
                ],
            )

        for step in plan:
            try:
                logger.info("Executing step: %s", json.dumps(step.model_dump()))

                if step.tool == "update_crm":
                    results.append(self.connector_hub.update_crm(step.payload))
                elif step.tool == "notify_team":
                    results.append(
                        self.connector_hub.notify_team(step.payload["message"])
                    )
            except Exception as exc:
                logger.exception("Connector step failed: %s", step.tool)
                results.append(
                    {
                        "status": "error",
                        "tool": step.tool,
                        "error": str(exc),
                    }
                )
                break

        return IntentExecutionResult(
            parsed_intent=parsed_intent,
            plan=plan,
            results=results,
        )
