from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="USV Notifications Service")


class NotificationDraft(BaseModel):
    user_email: str
    subject: str
    message: str


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "notifications-service"}


@app.post("/notifications/preview")
def preview_notification(payload: NotificationDraft) -> dict:
    # MVP endpoint that validates payload shape and can be replaced by real delivery later.
    return {
        "queued": False,
        "service": "notifications-service",
        "scheduled_for": datetime.now(timezone.utc).isoformat(),
        "payload": payload.model_dump(),
    }
