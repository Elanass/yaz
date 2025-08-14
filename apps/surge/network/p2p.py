"""
P2P Network Manager for Surge
Enables peer-to-peer collaboration between instances
"""

import asyncio
import json
import aiohttp
import socket
from typing import Dict, List, Set, Optional
from datetime import datetime
import hashlib

from shared.logging import get_logger
from shared.config import get_shared_config

logger = get_logger("surge.p2p")
config = get_shared_config()


class P2PNode:
    """A single P2P node in the surgery collaboration network"""
    
    def __init__(self, node_id: str = None, port: int = 8001):
        self.node_id = node_id or self.generate_node_id()
        self.port = port
        self.host = self.get_local_ip()
        self.peers: Dict[str, Dict] = {}
        self.surgery_data: Dict = {}
        self.session = None
        self.server_task = None
        
    def generate_node_id(self) -> str:
        """Generate unique node ID"""
        hostname = socket.gethostname()
        timestamp = str(datetime.now().timestamp())
        return hashlib.md5(f"{hostname}_{timestamp}".encode()).hexdigest()[:8]
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    async def start(self):
        """Start the P2P node"""
        self.session = aiohttp.ClientSession()
        self.server_task = asyncio.create_task(self.start_server())
        logger.info(f"P2P Node {self.node_id} started on {self.host}:{self.port}")
        
        # Try to discover and connect to other nodes
        await self.discover_peers()
    
    async def stop(self):
        """Stop the P2P node"""
        if self.server_task:
            self.server_task.cancel()
        if self.session:
            await self.session.close()
        logger.info(f"P2P Node {self.node_id} stopped")
    
    async def start_server(self):
        """Start HTTP server for P2P communication"""
        from aiohttp import web
        
        app = web.Application()
        app.router.add_get('/ping', self.handle_ping)
        app.router.add_post('/sync', self.handle_sync)
        app.router.add_post('/join', self.handle_join)
        app.router.add_get('/peers', self.handle_get_peers)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"P2P server running on http://{self.host}:{self.port}")
        
        # Keep server running
        while True:
            await asyncio.sleep(1)
    
    async def handle_ping(self, request):
        """Handle ping requests from other nodes"""
        from aiohttp import web
        return web.json_response({
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "status": "online",
            "surgery_cases": len(self.surgery_data)
        })
    
    async def handle_sync(self, request):
        """Handle data synchronization requests"""
        from aiohttp import web
        data = await request.json()
        
        # Merge surgery data from remote node
        remote_data = data.get("surgery_data", {})
        for case_id, case_data in remote_data.items():
            if case_id not in self.surgery_data:
                self.surgery_data[case_id] = case_data
                logger.info(f"Synced new case {case_id} from {data.get('node_id')}")
        
        return web.json_response({
            "status": "synced",
            "node_id": self.node_id,
            "cases_received": len(remote_data)
        })
    
    async def handle_join(self, request):
        """Handle requests from new nodes to join network"""
        from aiohttp import web
        data = await request.json()
        node_id = data.get("node_id")
        node_info = {
            "host": data.get("host"),
            "port": data.get("port"),
            "joined_at": datetime.now().isoformat()
        }
        
        self.peers[node_id] = node_info
        logger.info(f"Node {node_id} joined the network")
        
        # Send current peers list back
        return web.json_response({
            "status": "joined",
            "peers": self.peers,
            "surgery_data": self.surgery_data
        })
    
    async def handle_get_peers(self, request):
        """Return list of known peers"""
        from aiohttp import web
        return web.json_response({
            "node_id": self.node_id,
            "peers": self.peers
        })
    
    async def discover_peers(self):
        """Discover other P2P nodes on the network"""
        # Try common ports and IPs
        local_network = ".".join(self.host.split(".")[:-1]) + "."
        
        for i in range(1, 10):  # Limited discovery for demo
            ip = f"{local_network}{i}"
            if ip == self.host:
                continue
                
            for port in [8001, 8002, 8003]:
                if port == self.port:
                    continue
                    
                try:
                    await self.connect_to_peer(ip, port)
                except:
                    pass  # Continue discovery
    
    async def connect_to_peer(self, host: str, port: int):
        """Connect to a specific peer"""
        try:
            url = f"http://{host}:{port}/ping"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                if response.status == 200:
                    data = await response.json()
                    peer_id = data.get("node_id")
                    
                    if peer_id not in self.peers:
                        self.peers[peer_id] = {
                            "host": host,
                            "port": port,
                            "discovered_at": datetime.now().isoformat()
                        }
                        
                        # Join their network
                        await self.join_peer_network(host, port)
                        logger.info(f"Connected to peer {peer_id} at {host}:{port}")
                        
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logger.debug(f"Failed to connect to {host}:{port}: {e}")
    
    async def join_peer_network(self, host: str, port: int):
        """Join an existing peer's network"""
        try:
            url = f"http://{host}:{port}/join"
            payload = {
                "node_id": self.node_id,
                "host": self.host,
                "port": self.port
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Update peers list
                    new_peers = data.get("peers", {})
                    self.peers.update(new_peers)
                    
                    # Sync surgery data
                    remote_surgery_data = data.get("surgery_data", {})
                    self.surgery_data.update(remote_surgery_data)
                    
                    logger.info(f"Joined network with {len(new_peers)} peers")
                    
        except Exception as e:
            logger.error(f"Failed to join peer network at {host}:{port}: {e}")
    
    def add_surgery_case(self, case_data: Dict):
        """Add surgery case and broadcast to peers"""
        case_id = case_data.get("id")
        self.surgery_data[case_id] = case_data
        
        # Broadcast asynchronously
        asyncio.create_task(self.broadcast_surgery_data(case_data))
    
    async def broadcast_surgery_data(self, case_data: Dict):
        """Broadcast surgery case data to all peers"""
        for peer_id, peer_info in self.peers.items():
            try:
                url = f"http://{peer_info['host']}:{peer_info['port']}/sync"
                payload = {
                    "node_id": self.node_id,
                    "surgery_data": {case_data["id"]: case_data}
                }
                
                async with self.session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.debug(f"Synced data to peer {peer_id}")
                        
            except Exception as e:
                logger.error(f"Failed to sync with peer {peer_id}: {e}")
    
    def get_network_status(self) -> Dict:
        """Get current network status"""
        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port,
            "peers": len(self.peers),
            "surgery_cases": len(self.surgery_data),
            "peer_list": list(self.peers.keys())
        }


# Global P2P node instance
p2p_node: Optional[P2PNode] = None


async def initialize_p2p(port: int = 8001) -> P2PNode:
    """Initialize P2P networking"""
    global p2p_node
    
    if p2p_node is None:
        p2p_node = P2PNode(port=port)
        await p2p_node.start()
    
    return p2p_node


async def shutdown_p2p():
    """Shutdown P2P networking"""
    global p2p_node
    
    if p2p_node:
        await p2p_node.stop()
        p2p_node = None


def get_p2p_node() -> Optional[P2PNode]:
    """Get the current P2P node instance"""
    return p2p_node
