from types import SimpleNamespace

import pytest

from agents import GeminiIntentAgent, OrchestratorService, ParsedIntent


def make_gemini_response(name: str, args: dict) -> SimpleNamespace:
    return SimpleNamespace(
        candidates=[
            SimpleNamespace(
                content=SimpleNamespace(
                    parts=[SimpleNamespace(function_call=SimpleNamespace(name=name, args=args))]
                )
            )
        ]
    )


class FakeModels:
    def __init__(self, response: SimpleNamespace) -> None:
        self._response = response

    def generate_content(self, **_: object) -> SimpleNamespace:
        return self._response


class FakeClient:
    def __init__(self, response: SimpleNamespace) -> None:
        self.models = FakeModels(response)


class RecordingConnectorHub:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def update_crm(self, data: dict) -> dict:
        self.calls.append(("update_crm", data))
        return {"status": "success", "tool": "update_crm"}

    def notify_team(self, message: str) -> dict:
        self.calls.append(("notify_team", message))
        return {"status": "success", "tool": "notify_team"}


def test_parse_intent_uses_gemini_function_call_output() -> None:
    response = make_gemini_response(
        "parse_intent",
        {
            "task": "onboard_client",
            "target_platform": "crm_and_team_ops",
            "data": {
                "client_name": "Acme Corp",
                "requested_action": "onboard_new_client",
            },
        },
    )
    agent = GeminiIntentAgent(api_key="test-key", client=FakeClient(response))

    parsed = agent.parse_intent("Onboard a new client named Acme Corp")

    assert parsed == ParsedIntent(
        task="onboard_client",
        target_platform="crm_and_team_ops",
        data={
            "client_name": "Acme Corp",
            "requested_action": "onboard_new_client",
        },
    )


def test_build_execution_plan_for_onboarding_has_two_ordered_steps() -> None:
    agent = GeminiIntentAgent(api_key="test-key", client=object())
    parsed = ParsedIntent(
        task="onboard_client",
        target_platform="crm_and_team_ops",
        data={"client_name": "Acme Corp", "requested_action": "onboard_new_client"},
    )

    plan = agent.build_execution_plan(parsed)

    assert [step.tool for step in plan] == ["update_crm", "notify_team"]
    assert plan[1].payload["message"] == "New client onboarding started for Acme Corp."


def test_orchestrator_executes_connector_calls_in_sequence() -> None:
    response = make_gemini_response(
        "parse_intent",
        {
            "task": "onboard_client",
            "target_platform": "crm_and_team_ops",
            "data": {
                "client_name": "Acme Corp",
                "requested_action": "onboard_new_client",
            },
        },
    )
    connector_hub = RecordingConnectorHub()
    service = OrchestratorService(
        connector_hub=connector_hub,
        agent=GeminiIntentAgent(api_key="test-key", client=FakeClient(response)),
    )

    result = service.handle_intent("Onboard a new client named Acme Corp")

    assert connector_hub.calls == [
        (
            "update_crm",
            {"client_name": "Acme Corp", "requested_action": "onboard_new_client"},
        ),
        ("notify_team", "New client onboarding started for Acme Corp."),
    ]
    assert [item["status"] for item in result.results] == ["success", "success"]


def test_parse_intent_raises_when_gemini_returns_wrong_function() -> None:
    response = make_gemini_response("wrong_tool", {"task": "unknown"})
    agent = GeminiIntentAgent(api_key="test-key", client=FakeClient(response))

    with pytest.raises(ValueError, match="Unexpected Gemini function returned"):
        agent.parse_intent("Something else")
