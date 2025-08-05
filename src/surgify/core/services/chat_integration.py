"""
Chat Integration Service for Surgify Platform
Handles Chatwoot and Discord integrations for chat features
"""

import logging
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import os

from .base import BaseService
from .logger import get_logger

logger = get_logger(__name__)


class ChatIntegrationService(BaseService):
    """
    Unified chat service for Chatwoot and Discord integrations
    """

    def __init__(self):
        super().__init__()
        self.chatwoot_config = {
            "base_url": os.getenv("CHATWOOT_BASE_URL", "https://app.chatwoot.com"),
            "account_id": os.getenv("CHATWOOT_ACCOUNT_ID"),
            "access_token": os.getenv("CHATWOOT_ACCESS_TOKEN"),
            "inbox_id": os.getenv("CHATWOOT_INBOX_ID"),
        }

        self.discord_config = {
            "bot_token": os.getenv("DISCORD_BOT_TOKEN"),
            "guild_id": os.getenv("DISCORD_GUILD_ID"),
            "channel_id": os.getenv("DISCORD_CHANNEL_ID"),
            "webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
        }

    async def initialize_chatwoot(self) -> bool:
        """Initialize Chatwoot integration"""
        try:
            if not all(
                [
                    self.chatwoot_config["account_id"],
                    self.chatwoot_config["access_token"],
                    self.chatwoot_config["inbox_id"],
                ]
            ):
                logger.warning("Chatwoot configuration incomplete")
                return False

            # Test connection
            headers = {"api_access_token": self.chatwoot_config["access_token"]}
            url = f"{self.chatwoot_config['base_url']}/api/v1/accounts/{self.chatwoot_config['account_id']}/profile"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        logger.info("Chatwoot integration initialized successfully")
                        return True
                    else:
                        logger.error(f"Chatwoot connection failed: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Failed to initialize Chatwoot: {str(e)}")
            return False

    async def initialize_discord(self) -> bool:
        """Initialize Discord integration"""
        try:
            if not self.discord_config["bot_token"]:
                logger.warning("Discord bot token not configured")
                return False

            # Test webhook if available
            if self.discord_config["webhook_url"]:
                test_payload = {
                    "content": "🔧 Surgify chat integration initialized",
                    "embeds": [
                        {
                            "title": "System Status",
                            "description": "Chat features are now active",
                            "color": 0x00FF00,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    ],
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.discord_config["webhook_url"], json=test_payload
                    ) as response:
                        if response.status in [200, 204]:
                            logger.info("Discord integration initialized successfully")
                            return True
                        else:
                            logger.error(
                                f"Discord webhook test failed: {response.status}"
                            )
                            return False

            logger.info("Discord configured (bot mode)")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Discord: {str(e)}")
            return False

    async def send_chatwoot_message(
        self, conversation_id: int, content: str, message_type: str = "outgoing"
    ) -> Dict[str, Any]:
        """Send message via Chatwoot"""
        try:
            headers = {
                "api_access_token": self.chatwoot_config["access_token"],
                "Content-Type": "application/json",
            }

            payload = {
                "content": content,
                "message_type": message_type,
                "private": False,
            }

            url = f"{self.chatwoot_config['base_url']}/api/v1/accounts/{self.chatwoot_config['account_id']}/conversations/{conversation_id}/messages"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(
                            f"Chatwoot message sent to conversation {conversation_id}"
                        )
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Failed to send Chatwoot message: {response.status} - {error_text}"
                        )
                        return {"error": error_text}

        except Exception as e:
            logger.error(f"Chatwoot message error: {str(e)}")
            return {"error": str(e)}

    async def send_discord_message(
        self, content: str, channel_id: str = None, embed: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send message via Discord"""
        try:
            if not channel_id:
                channel_id = self.discord_config["channel_id"]

            if self.discord_config["webhook_url"]:
                # Use webhook for simpler integration
                payload = {"content": content}
                if embed:
                    payload["embeds"] = [embed]

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.discord_config["webhook_url"], json=payload
                    ) as response:
                        if response.status in [200, 204]:
                            logger.info("Discord message sent via webhook")
                            return {"success": True}
                        else:
                            error_text = await response.text()
                            logger.error(
                                f"Discord webhook failed: {response.status} - {error_text}"
                            )
                            return {"error": error_text}
            else:
                # Use bot API
                headers = {
                    "Authorization": f'Bot {self.discord_config["bot_token"]}',
                    "Content-Type": "application/json",
                }

                payload = {"content": content}
                if embed:
                    payload["embeds"] = [embed]

                url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url, headers=headers, json=payload
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.info(f"Discord message sent to channel {channel_id}")
                            return result
                        else:
                            error_text = await response.text()
                            logger.error(
                                f"Discord API error: {response.status} - {error_text}"
                            )
                            return {"error": error_text}

        except Exception as e:
            logger.error(f"Discord message error: {str(e)}")
            return {"error": str(e)}

    async def create_discord_invite(
        self, max_age: int = 86400, max_uses: int = 10
    ) -> Optional[str]:
        """Create Discord server invite link"""
        try:
            if (
                not self.discord_config["bot_token"]
                or not self.discord_config["channel_id"]
            ):
                logger.warning("Discord not properly configured for invite creation")
                return None

            headers = {
                "Authorization": f'Bot {self.discord_config["bot_token"]}',
                "Content-Type": "application/json",
            }

            payload = {
                "max_age": max_age,
                "max_uses": max_uses,
                "temporary": False,
                "unique": True,
            }

            url = f"https://discord.com/api/v10/channels/{self.discord_config['channel_id']}/invites"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        invite_url = f"https://discord.gg/{result['code']}"
                        logger.info(f"Created Discord invite: {invite_url}")
                        return invite_url
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Failed to create Discord invite: {response.status} - {error_text}"
                        )
                        return None

        except Exception as e:
            logger.error(f"Discord invite creation error: {str(e)}")
            return None

    async def handle_case_notification(
        self, case_id: int, event_type: str, data: Dict[str, Any]
    ) -> None:
        """Send case notifications to both Chatwoot and Discord"""
        try:
            message_content = self._format_case_message(case_id, event_type, data)

            # Send to Discord
            embed = {
                "title": f"Case {case_id} - {event_type.title().replace('_', ' ')}",
                "description": message_content,
                "color": self._get_event_color(event_type),
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {"name": "Case ID", "value": str(case_id), "inline": True},
                    {"name": "Event", "value": event_type, "inline": True},
                ],
            }

            await self.send_discord_message(
                content=f"📋 Case Update: {case_id}", embed=embed
            )

            # Send to Chatwoot if there's an active conversation
            if "conversation_id" in data:
                await self.send_chatwoot_message(
                    conversation_id=data["conversation_id"], content=message_content
                )

        except Exception as e:
            logger.error(f"Failed to send case notification: {str(e)}")

    def _format_case_message(
        self, case_id: int, event_type: str, data: Dict[str, Any]
    ) -> str:
        """Format case event message"""
        messages = {
            "created": f"New case #{case_id} has been created",
            "updated": f"Case #{case_id} has been updated",
            "status_changed": f"Case #{case_id} status changed to {data.get('status', 'unknown')}",
            "comment_added": f"New comment added to case #{case_id}",
            "assigned": f"Case #{case_id} assigned to {data.get('assignee', 'someone')}",
        }

        base_message = messages.get(event_type, f"Case #{case_id} event: {event_type}")

        if "title" in data:
            base_message += f"\nTitle: {data['title']}"

        if "priority" in data:
            base_message += f"\nPriority: {data['priority']}"

        return base_message

    def _get_event_color(self, event_type: str) -> int:
        """Get color for Discord embed based on event type"""
        colors = {
            "created": 0x00FF00,  # Green
            "updated": 0x0099FF,  # Blue
            "status_changed": 0xFF9900,  # Orange
            "comment_added": 0x9900FF,  # Purple
            "assigned": 0x00FFFF,  # Cyan
            "error": 0xFF0000,  # Red
        }
        return colors.get(event_type, 0x808080)  # Gray default

    async def get_chat_stats(self) -> Dict[str, Any]:
        """Get statistics from both chat platforms"""
        stats = {
            "chatwoot": {"status": "disconnected", "conversations": 0},
            "discord": {"status": "disconnected", "members": 0},
            "last_updated": datetime.utcnow().isoformat(),
        }

        # Get Chatwoot stats
        try:
            if await self.initialize_chatwoot():
                headers = {"api_access_token": self.chatwoot_config["access_token"]}
                url = f"{self.chatwoot_config['base_url']}/api/v1/accounts/{self.chatwoot_config['account_id']}/conversations"

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            stats["chatwoot"] = {
                                "status": "connected",
                                "conversations": len(result.get("data", [])),
                            }
        except Exception as e:
            logger.error(f"Failed to get Chatwoot stats: {str(e)}")

        # Get Discord stats
        try:
            if self.discord_config["bot_token"] and self.discord_config["guild_id"]:
                headers = {"Authorization": f'Bot {self.discord_config["bot_token"]}'}
                url = f"https://discord.com/api/v10/guilds/{self.discord_config['guild_id']}"

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            stats["discord"] = {
                                "status": "connected",
                                "members": result.get("member_count", 0),
                            }
        except Exception as e:
            logger.error(f"Failed to get Discord stats: {str(e)}")

        return stats
