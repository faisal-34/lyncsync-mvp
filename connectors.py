import logging
from typing import Any, Dict


logger = logging.getLogger(__name__)


class ConnectorHub:
    """Mock integration layer for enterprise system connectors."""

    def update_crm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Updating CRM with payload: %s", data)

        if not data.get("client_name"):
            raise ValueError("CRM update requires a client_name field.")

        return {
            "status": "success",
            "system": "crm",
            "action": "update_client_record",
            "data": data,
        }

    def notify_team(self, message: str) -> Dict[str, Any]:
        logger.info("Sending team notification: %s", message)

        if not message.strip():
            raise ValueError("Notification message cannot be empty.")

        return {
            "status": "success",
            "system": "team_messaging",
            "action": "notify_team",
            "message": message,
        }
