"""Chat Integration API Endpoints
Provides REST API for Chatwoot and Discord integrations.
"""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from apps.surge.core.services.chat_integration import ChatIntegrationService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# Global chat service instance
chat_service = ChatIntegrationService()


@router.on_event("startup")
async def initialize_chat_services() -> None:
    """Initialize chat services on startup."""
    try:
        await chat_service.initialize_chatwoot()
        await chat_service.initialize_discord()
        logger.info("Chat services initialized successfully")
    except Exception as e:
        logger.exception(f"Failed to initialize chat services: {e!s}")


@router.get("/stats")
async def get_chat_stats():
    """Get current chat platform statistics."""
    try:
        return await chat_service.get_chat_stats()
    except Exception as e:
        logger.exception(f"Failed to get chat stats: {e!s}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve chat statistics"
        )


@router.post("/chatwoot/message")
async def send_chatwoot_message(
    conversation_id: int, content: str, message_type: str = "outgoing"
):
    """Send a message via Chatwoot."""
    try:
        result = await chat_service.send_chatwoot_message(
            conversation_id=conversation_id, content=content, message_type=message_type
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"success": True, "data": result}
    except Exception as e:
        logger.exception(f"Failed to send Chatwoot message: {e!s}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.post("/discord/message")
async def send_discord_message(
    content: str,
    channel_id: str | None = None,
    embed: dict[str, Any] | None = None,
):
    """Send a message via Discord."""
    try:
        result = await chat_service.send_discord_message(
            content=content, channel_id=channel_id, embed=embed
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {"success": True, "data": result}
    except Exception as e:
        logger.exception(f"Failed to send Discord message: {e!s}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.post("/discord/invite")
async def create_discord_invite(max_age: int = 86400, max_uses: int = 10):
    """Create a Discord server invite link."""
    try:
        invite_url = await chat_service.create_discord_invite(
            max_age=max_age, max_uses=max_uses
        )

        if not invite_url:
            raise HTTPException(status_code=503, detail="Discord service unavailable")

        return {"invite_url": invite_url}
    except Exception as e:
        logger.exception(f"Failed to create Discord invite: {e!s}")
        raise HTTPException(status_code=500, detail="Failed to create invite")


@router.post("/notify/case/{case_id}")
async def notify_case_event(
    case_id: int,
    event_type: str,
    data: dict[str, Any],
    background_tasks: BackgroundTasks,
):
    """Send case event notifications to chat platforms."""
    try:
        background_tasks.add_task(
            chat_service.handle_case_notification,
            case_id=case_id,
            event_type=event_type,
            data=data,
        )

        return {"success": True, "message": "Notification sent"}
    except Exception as e:
        logger.exception(f"Failed to send case notification: {e!s}")
        raise HTTPException(status_code=500, detail="Failed to send notification")


@router.get("/health")
async def chat_health_check():
    """Health check for chat services."""
    try:
        chatwoot_healthy = await chat_service.initialize_chatwoot()
        discord_healthy = await chat_service.initialize_discord()

        return {
            "status": "healthy"
            if (chatwoot_healthy or discord_healthy)
            else "unhealthy",
            "services": {
                "chatwoot": "healthy" if chatwoot_healthy else "unhealthy",
                "discord": "healthy" if discord_healthy else "unhealthy",
            },
        }
    except Exception as e:
        logger.exception(f"Chat health check failed: {e!s}")
        return {"status": "unhealthy", "error": str(e)}
