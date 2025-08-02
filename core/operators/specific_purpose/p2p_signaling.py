"""
P2P WebRTC Signaling Server Operator
Handles WebSocket connections for peer-to-peer collaboration in the Gastric ADCI Platform
"""

import json
import asyncio
import uuid
from typing import Dict, Set, Optional, Any, List
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from starlette.websockets import WebSocketState

from core.operators.base_operator import BaseOperator
from core.services.logger import get_logger

logger = get_logger(__name__)


class P2pSignalingOperator(BaseOperator):
    """
    P2P Signaling Operator for WebRTC peer connections
    Manages WebSocket connections and facilitates SDP/ICE candidate exchange
    """
    
    def __init__(self):
        super().__init__()
        self.router = APIRouter(prefix="/p2p", tags=["P2P Signaling"])
        self.active_connections: Dict[str, WebSocket] = {}
        self.peer_rooms: Dict[str, Set[str]] = {}  # room_id -> set of peer_ids
        self.peer_metadata: Dict[str, Dict[str, Any]] = {}
        self.connection_status = "initializing"
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup API routes for P2P signaling"""
        
        @self.router.websocket("/ws/peer")
        async def websocket_peer_endpoint(websocket: WebSocket):
            await self.handle_peer_connection(websocket)
            
        @self.router.get("/peers")
        async def get_active_peers():
            """Get list of active peers"""
            return JSONResponse({
                "success": True,
                "data": {
                    "active_peers": len(self.active_connections),
                    "rooms": {room_id: len(peers) for room_id, peers in self.peer_rooms.items()},
                    "peer_metadata": {
                        peer_id: {
                            "user_id": meta.get("user_id"),
                            "room": meta.get("room"),
                            "connected_at": meta.get("connected_at"),
                            "last_seen": meta.get("last_seen")
                        }
                        for peer_id, meta in self.peer_metadata.items()
                    }
                }
            })
            
        @self.router.post("/rooms/{room_id}/broadcast")
        async def broadcast_to_room(room_id: str, message: Dict[str, Any]):
            """Broadcast message to all peers in a room"""
            if room_id not in self.peer_rooms:
                return JSONResponse({"success": False, "error": "Room not found"})
                
            peers_notified = await self.broadcast_to_room(room_id, message)
            return JSONResponse({
                "success": True,
                "data": {"peers_notified": peers_notified}
            })

    async def handle_peer_connection(self, websocket: WebSocket):
        """Handle individual peer WebSocket connection"""
        peer_id = str(uuid.uuid4())
        
        try:
            await websocket.accept()
            self.active_connections[peer_id] = websocket
            
            logger.info(f"Peer {peer_id} connected")
            
            # Send connection confirmation
            await self._send_to_peer(peer_id, {
                "type": "connection_established",
                "peer_id": peer_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Handle messages from this peer
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_peer_message(peer_id, message)
                    
                except WebSocketDisconnect:
                    logger.info(f"Peer {peer_id} disconnected")
                    break
                except json.JSONDecodeError:
                    await self._send_error(peer_id, "Invalid JSON message")
                except Exception as e:
                    logger.error(f"Error handling message from peer {peer_id}: {e}")
                    await self._send_error(peer_id, f"Message handling error: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error in peer connection {peer_id}: {e}")
        finally:
            await self._cleanup_peer(peer_id)

    async def _handle_peer_message(self, peer_id: str, message: Dict[str, Any]):
        """Handle incoming message from a peer"""
        message_type = message.get("type")
        
        # Update last seen
        if peer_id in self.peer_metadata:
            self.peer_metadata[peer_id]["last_seen"] = datetime.utcnow().isoformat()
        
        if message_type == "join_room":
            await self._handle_join_room(peer_id, message)
        elif message_type == "leave_room":
            await self._handle_leave_room(peer_id, message)
        elif message_type == "offer":
            await self._handle_webrtc_offer(peer_id, message)
        elif message_type == "answer":
            await self._handle_webrtc_answer(peer_id, message)
        elif message_type == "ice_candidate":
            await self._handle_ice_candidate(peer_id, message)
        elif message_type == "data_sync":
            await self._handle_data_sync(peer_id, message)
        elif message_type == "heartbeat":
            await self._handle_heartbeat(peer_id, message)
        else:
            await self._send_error(peer_id, f"Unknown message type: {message_type}")

    async def _handle_join_room(self, peer_id: str, message: Dict[str, Any]):
        """Handle peer joining a room"""
        room_id = message.get("room_id")
        user_metadata = message.get("metadata", {})
        
        if not room_id:
            await self._send_error(peer_id, "Room ID required")
            return
            
        # Initialize room if it doesn't exist
        if room_id not in self.peer_rooms:
            self.peer_rooms[room_id] = set()
            
        # Add peer to room
        self.peer_rooms[room_id].add(peer_id)
        
        # Store peer metadata
        self.peer_metadata[peer_id] = {
            "room": room_id,
            "user_id": user_metadata.get("user_id"),
            "user_name": user_metadata.get("user_name"),
            "connected_at": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            **user_metadata
        }
        
        # Notify peer of successful room join
        await self._send_to_peer(peer_id, {
            "type": "room_joined",
            "room_id": room_id,
            "peer_count": len(self.peer_rooms[room_id])
        })
        
        # Notify other peers in room
        await self._broadcast_to_room_except_sender(room_id, peer_id, {
            "type": "peer_joined",
            "peer_id": peer_id,
            "metadata": user_metadata,
            "peer_count": len(self.peer_rooms[room_id])
        })
        
        logger.info(f"Peer {peer_id} joined room {room_id}")

    async def _handle_leave_room(self, peer_id: str, message: Dict[str, Any]):
        """Handle peer leaving a room"""
        room_id = message.get("room_id")
        
        if not room_id or room_id not in self.peer_rooms:
            return
            
        if peer_id in self.peer_rooms[room_id]:
            self.peer_rooms[room_id].remove(peer_id)
            
            # Clean up empty rooms
            if not self.peer_rooms[room_id]:
                del self.peer_rooms[room_id]
                
            # Notify other peers
            await self._broadcast_to_room_except_sender(room_id, peer_id, {
                "type": "peer_left",
                "peer_id": peer_id,
                "peer_count": len(self.peer_rooms.get(room_id, set()))
            })
            
        # Update peer metadata
        if peer_id in self.peer_metadata:
            self.peer_metadata[peer_id]["room"] = None
            
        logger.info(f"Peer {peer_id} left room {room_id}")

    async def _handle_webrtc_offer(self, peer_id: str, message: Dict[str, Any]):
        """Handle WebRTC offer for direct peer connection"""
        target_peer_id = message.get("target_peer_id")
        offer = message.get("offer")
        
        if not target_peer_id or not offer:
            await self._send_error(peer_id, "Target peer ID and offer required")
            return
            
        if target_peer_id not in self.active_connections:
            await self._send_error(peer_id, "Target peer not found")
            return
            
        # Forward offer to target peer
        await self._send_to_peer(target_peer_id, {
            "type": "offer",
            "from_peer_id": peer_id,
            "offer": offer,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Forwarded WebRTC offer from {peer_id} to {target_peer_id}")

    async def _handle_webrtc_answer(self, peer_id: str, message: Dict[str, Any]):
        """Handle WebRTC answer for direct peer connection"""
        target_peer_id = message.get("target_peer_id")
        answer = message.get("answer")
        
        if not target_peer_id or not answer:
            await self._send_error(peer_id, "Target peer ID and answer required")
            return
            
        if target_peer_id not in self.active_connections:
            await self._send_error(peer_id, "Target peer not found")
            return
            
        # Forward answer to target peer
        await self._send_to_peer(target_peer_id, {
            "type": "answer",
            "from_peer_id": peer_id,
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Forwarded WebRTC answer from {peer_id} to {target_peer_id}")

    async def _handle_ice_candidate(self, peer_id: str, message: Dict[str, Any]):
        """Handle ICE candidate for WebRTC connection"""
        target_peer_id = message.get("target_peer_id")
        candidate = message.get("candidate")
        
        if not target_peer_id:
            await self._send_error(peer_id, "Target peer ID required")
            return
            
        if target_peer_id not in self.active_connections:
            # ICE candidates can arrive after peer disconnects, so just log
            logger.debug(f"ICE candidate for disconnected peer {target_peer_id}")
            return
            
        # Forward ICE candidate to target peer
        await self._send_to_peer(target_peer_id, {
            "type": "ice_candidate",
            "from_peer_id": peer_id,
            "candidate": candidate,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _handle_data_sync(self, peer_id: str, message: Dict[str, Any]):
        """Handle collaborative data synchronization"""
        room_id = self.peer_metadata.get(peer_id, {}).get("room")
        
        if not room_id:
            await self._send_error(peer_id, "Not in a room")
            return
            
        # Broadcast data sync to all peers in room except sender
        await self._broadcast_to_room_except_sender(room_id, peer_id, {
            "type": "data_sync",
            "from_peer_id": peer_id,
            "data": message.get("data"),
            "sync_type": message.get("sync_type"),
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _handle_heartbeat(self, peer_id: str, message: Dict[str, Any]):
        """Handle heartbeat to keep connection alive"""
        await self._send_to_peer(peer_id, {
            "type": "heartbeat_ack",
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _send_to_peer(self, peer_id: str, message: Dict[str, Any]):
        """Send message to a specific peer"""
        if peer_id not in self.active_connections:
            return False
            
        websocket = self.active_connections[peer_id]
        
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(message))
                return True
        except Exception as e:
            logger.error(f"Error sending message to peer {peer_id}: {e}")
            await self._cleanup_peer(peer_id)
            
        return False

    async def _send_error(self, peer_id: str, error_message: str):
        """Send error message to peer"""
        await self._send_to_peer(peer_id, {
            "type": "error",
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _broadcast_to_room_except_sender(self, room_id: str, sender_peer_id: str, message: Dict[str, Any]):
        """Broadcast message to all peers in room except sender"""
        if room_id not in self.peer_rooms:
            return 0
            
        peers_notified = 0
        for peer_id in self.peer_rooms[room_id]:
            if peer_id != sender_peer_id:
                if await self._send_to_peer(peer_id, message):
                    peers_notified += 1
                    
        return peers_notified

    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any]) -> int:
        """Broadcast message to all peers in a room (public method)"""
        if room_id not in self.peer_rooms:
            return 0
            
        peers_notified = 0
        for peer_id in self.peer_rooms[room_id]:
            if await self._send_to_peer(peer_id, message):
                peers_notified += 1
                
        return peers_notified

    async def _cleanup_peer(self, peer_id: str):
        """Clean up peer connection and metadata"""
        # Remove from active connections
        if peer_id in self.active_connections:
            del self.active_connections[peer_id]
            
        # Remove from rooms
        peer_room = None
        if peer_id in self.peer_metadata:
            peer_room = self.peer_metadata[peer_id].get("room")
            
        if peer_room and peer_room in self.peer_rooms:
            if peer_id in self.peer_rooms[peer_room]:
                self.peer_rooms[peer_room].remove(peer_id)
                
                # Notify other peers in room
                await self._broadcast_to_room_except_sender(peer_room, peer_id, {
                    "type": "peer_disconnected",
                    "peer_id": peer_id,
                    "peer_count": len(self.peer_rooms[peer_room])
                })
                
                # Clean up empty rooms
                if not self.peer_rooms[peer_room]:
                    del self.peer_rooms[peer_room]
        
        # Remove metadata
        if peer_id in self.peer_metadata:
            del self.peer_metadata[peer_id]
            
        logger.info(f"Cleaned up peer {peer_id}")

    async def initialize(self) -> bool:
        """Initialize the P2P signaling operator"""
        try:
            self.connection_status = "active"
            logger.info("P2P Signaling Operator initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize P2P Signaling Operator: {e}")
            self.connection_status = "failed"
            return False

    async def cleanup(self):
        """Clean up all connections and resources"""
        # Notify all peers of shutdown
        shutdown_message = {
            "type": "server_shutdown",
            "message": "P2P signaling server is shutting down",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for peer_id in list(self.active_connections.keys()):
            await self._send_to_peer(peer_id, shutdown_message)
            await self._cleanup_peer(peer_id)
            
        self.connection_status = "stopped"
        logger.info("P2P Signaling Operator cleaned up")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of P2P signaling server"""
        return {
            "status": self.connection_status,
            "active_connections": len(self.active_connections),
            "active_rooms": len(self.peer_rooms),
            "total_peers_in_rooms": sum(len(peers) for peers in self.peer_rooms.values())
        }

    def get_router(self) -> APIRouter:
        """Get the FastAPI router for P2P endpoints"""
        return self.router
