import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents import OrchestratorService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LyncSync MVP",
    description="AI Agentic Orchestrator for intent-to-action workflows.",
    version="0.1.0",
)

orchestrator = OrchestratorService()


class IntentRequest(BaseModel):
    user_intent: str = Field(
        ...,
        min_length=3,
        description="Natural language instruction to be interpreted by the agent.",
    )


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/orchestrate")
def orchestrate_intent(request: IntentRequest) -> dict:
    logger.info("Received orchestration request.")

    try:
        execution_result = orchestrator.handle_intent(request.user_intent)
        return {
            "status": "success",
            "execution": execution_result.model_dump(),
        }
    except ValueError as exc:
        logger.warning("Validation-style orchestration error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unhandled orchestration failure.")
        raise HTTPException(
            status_code=500,
            detail="Internal orchestration error.",
        ) from exc
