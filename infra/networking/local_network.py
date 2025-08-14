"""Local Network Manager for team collaboration
Enables mDNS discovery and WebRTC connections.
"""

import asyncio
import json
import logging
import socket
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import netifaces
import websockets


logger = logging.getLogger(__name__)


@dataclass
class LocalPeer:
    """Represents a local network peer."""

    id: str
    name: str
    ip: str
    port: int
    capabilities: list[str]
    last_seen: datetime
    websocket: Optional = None


class LocalNetworkManager:
    """Manages local network discovery and collaboration."""

    def __init__(self, port: int = 8001) -> None:
        self.port = port
        self.peers: dict[str, LocalPeer] = {}
        self.server = None
        self.discovery_running = False
        self.callbacks = {}

    async def start(self) -> None:
        """Start local network services."""
        logger.info("🌐 Starting Local Network Manager...")

        # Start WebSocket server for peer connections
        await self._start_websocket_server()

        # Start mDNS discovery
        await self._start_mdns_discovery()

        # Start peer health monitoring
        asyncio.create_task(self._monitor_peers())

        logger.info(f"✅ Local Network Manager started on port {self.port}")

    async def _start_websocket_server(self) -> None:
        """Start WebSocket server for peer connections."""

        async def handle_client(websocket, path) -> None:
            try:
                peer_id = None
                async for message in websocket:
                    data = json.loads(message)

                    if data["type"] == "handshake":
                        peer_id = data["peer_id"]
                        peer = LocalPeer(
                            id=peer_id,
                            name=data["name"],
                            ip=websocket.remote_address[0],
                            port=data["port"],
                            capabilities=data["capabilities"],
                            last_seen=datetime.now(),
                            websocket=websocket,
                        )
                        self.peers[peer_id] = peer
                        logger.info(f"🤝 New peer connected: {peer.name} ({peer.ip})")

                        # Notify callbacks
                        if "peer_connected" in self.callbacks:
                            await self.callbacks["peer_connected"](peer)

                    elif data["type"] == "collaboration_data":
                        # Handle collaboration data
                        if "collaboration_update" in self.callbacks:
                            await self.callbacks["collaboration_update"](data)

            except websockets.exceptions.ConnectionClosed:
                if peer_id and peer_id in self.peers:
                    logger.info(f"👋 Peer disconnected: {self.peers[peer_id].name}")
                    del self.peers[peer_id]

        self.server = await websockets.serve(handle_client, "0.0.0.0", self.port)

    async def _start_mdns_discovery(self) -> None:
        """Start mDNS service discovery."""
        # Simplified mDNS-like discovery using UDP broadcast
        self.discovery_running = True

        async def discovery_loop() -> None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Get local IP
            local_ip = self._get_local_ip()

            while self.discovery_running:
                try:
                    # Broadcast presence
                    discovery_msg = {
                        "type": "yaz_discovery",
                        "peer_id": f"yaz_{local_ip}_{self.port}",
                        "name": f"Yaz-{local_ip}",
                        "ip": local_ip,
                        "port": self.port,
                        "capabilities": ["surgery", "analytics", "collaboration"],
                        "timestamp": datetime.now().isoformat(),
                    }

                    sock.sendto(
                        json.dumps(discovery_msg).encode(), ("255.255.255.255", 8002)
                    )
                    await asyncio.sleep(10)  # Broadcast every 10 seconds

                except Exception as e:
                    logger.exception(f"Discovery broadcast error: {e}")
                    await asyncio.sleep(5)

        asyncio.create_task(discovery_loop())

    def _get_local_ip(self) -> str:
        """Get local IP address."""
        try:
            # Try to get the IP from network interfaces
            interfaces = netifaces.interfaces()
            for interface in interfaces:
                if interface.startswith(("eth", "wlan")):
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        return addrs[netifaces.AF_INET][0]["addr"]
        except:
            pass

        # Fallback method
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"

    async def _monitor_peers(self) -> None:
        """Monitor peer health and connectivity."""
        while True:
            try:
                current_time = datetime.now()
                stale_peers = []

                for peer_id, peer in self.peers.items():
                    # Check if peer is stale (no activity for 30 seconds)
                    if (current_time - peer.last_seen).seconds > 30:
                        stale_peers.append(peer_id)

                # Remove stale peers
                for peer_id in stale_peers:
                    if peer_id in self.peers:
                        logger.info(
                            f"🕰️ Removing stale peer: {self.peers[peer_id].name}"
                        )
                        del self.peers[peer_id]

                await asyncio.sleep(15)  # Check every 15 seconds

            except Exception as e:
                logger.exception(f"Peer monitoring error: {e}")
                await asyncio.sleep(10)

    async def discover_local_peers(self) -> list[LocalPeer]:
        """Discover local team members on same network."""
        return list(self.peers.values())

    async def setup_local_collaboration(self) -> None:
        """Enable real-time local collaboration."""
        logger.info("🤝 Setting up local collaboration...")

        # Register collaboration callbacks
        self.callbacks["peer_connected"] = self._on_peer_connected
        self.callbacks["collaboration_update"] = self._on_collaboration_update

    async def _on_peer_connected(self, peer: LocalPeer) -> None:
        """Handle new peer connection."""
        logger.info(
            f"🎯 New collaborator: {peer.name} with capabilities: {peer.capabilities}"
        )

    async def _on_collaboration_update(self, data: dict) -> None:
        """Handle collaboration data updates."""
        logger.info(f"🔄 Collaboration update: {data['action']}")

        # Broadcast to other peers
        await self.broadcast_to_peers(data)

    async def broadcast_to_peers(self, data: dict) -> None:
        """Broadcast data to all connected peers."""
        disconnected_peers = []

        for peer_id, peer in self.peers.items():
            if peer.websocket:
                try:
                    await peer.websocket.send(json.dumps(data))
                except:
                    disconnected_peers.append(peer_id)

        # Clean up disconnected peers
        for peer_id in disconnected_peers:
            if peer_id in self.peers:
                del self.peers[peer_id]

    async def connect_to_peer(self, ip: str, port: int) -> bool:
        """Connect to a specific peer."""
        try:
            uri = f"ws://{ip}:{port}"
            websocket = await websockets.connect(uri)

            # Send handshake
            handshake = {
                "type": "handshake",
                "peer_id": f"yaz_{self._get_local_ip()}_{self.port}",
                "name": f"Yaz-{self._get_local_ip()}",
                "port": self.port,
                "capabilities": ["surgery", "analytics", "collaboration"],
            }

            await websocket.send(json.dumps(handshake))
            logger.info(f"🔗 Connected to peer at {ip}:{port}")
            return True

        except Exception as e:
            logger.exception(f"Failed to connect to peer {ip}:{port}: {e}")
            return False

    async def stop(self) -> None:
        """Stop local network services."""
        logger.info("🛑 Stopping Local Network Manager...")

        self.discovery_running = False

        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # Close all peer connections
        for peer in self.peers.values():
            if peer.websocket:
                await peer.websocket.close()

        self.peers.clear()
        logger.info("✅ Local Network Manager stopped")
