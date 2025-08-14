"""P2P Network Manager with BitTorrent-inspired architecture
Implements DHT, peer discovery, and distributed data sync.
"""

import asyncio
import hashlib
import logging
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

import aiohttp
from cryptography.fernet import Fernet


logger = logging.getLogger(__name__)


@dataclass
class P2PPeer:
    """Represents a P2P network peer."""

    id: str
    address: str
    port: int
    last_seen: datetime
    capabilities: list[str]
    distance: int = 0  # XOR distance for DHT


@dataclass
class DataChunk:
    """Represents a chunk of data in the P2P network."""

    chunk_id: str
    data_id: str
    index: int
    data: bytes
    checksum: str
    size: int


class DHTNode:
    """Distributed Hash Table node."""

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self.routing_table: dict[str, P2PPeer] = {}
        self.data_store: dict[str, any] = {}
        self.k_bucket_size = 20  # Maximum peers per bucket

    def calculate_distance(self, other_id: str) -> int:
        """Calculate XOR distance between node IDs."""
        return int(self.node_id, 16) ^ int(other_id, 16)

    def add_peer(self, peer: P2PPeer) -> None:
        """Add peer to routing table."""
        peer.distance = self.calculate_distance(peer.id)
        self.routing_table[peer.id] = peer

        # Limit bucket size
        if len(self.routing_table) > self.k_bucket_size:
            # Remove oldest peer
            oldest = min(self.routing_table.values(), key=lambda p: p.last_seen)
            del self.routing_table[oldest.id]

    def find_closest_peers(self, target_id: str, count: int = 10) -> list[P2PPeer]:
        """Find closest peers to target ID."""
        target_distance = int(target_id, 16)

        peers_with_distance = []
        for peer in self.routing_table.values():
            distance = target_distance ^ int(peer.id, 16)
            peers_with_distance.append((distance, peer))

        # Sort by distance and return closest
        peers_with_distance.sort(key=lambda x: x[0])
        return [peer for _, peer in peers_with_distance[:count]]


class P2PNetworkManager:
    """Manages P2P networking with BitTorrent-inspired features."""

    def __init__(self, port: int = 8003) -> None:
        self.port = port
        self.node_id = self._generate_node_id()
        self.dht = DHTNode(self.node_id)
        self.server = None
        self.session = None
        self.running = False
        self.data_chunks: dict[str, dict[int, DataChunk]] = {}
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

    def _generate_node_id(self) -> str:
        """Generate unique node ID."""
        import uuid

        return hashlib.sha1(str(uuid.uuid4()).encode()).hexdigest()

    async def initialize_dht(self) -> None:
        """Initialize Distributed Hash Table."""
        logger.info("🌐 Initializing DHT...")

        # Start HTTP server for P2P communication
        await self._start_p2p_server()

        # Bootstrap with known peers (in production, use bootstrap servers)
        await self._bootstrap_network()

        # Start periodic maintenance
        asyncio.create_task(self._maintain_dht())

        logger.info(f"✅ DHT initialized with node ID: {self.node_id[:8]}...")

    async def _start_p2p_server(self) -> None:
        """Start HTTP server for P2P communication."""
        from aiohttp import web

        app = web.Application()
        app.router.add_post("/p2p/ping", self._handle_ping)
        app.router.add_post("/p2p/find_node", self._handle_find_node)
        app.router.add_post("/p2p/store", self._handle_store)
        app.router.add_post("/p2p/find_value", self._handle_find_value)
        app.router.add_post("/p2p/chunk_request", self._handle_chunk_request)
        app.router.add_post("/p2p/chunk_response", self._handle_chunk_response)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()

        self.running = True
        logger.info(f"🚀 P2P server started on port {self.port}")

    async def _bootstrap_network(self) -> None:
        """Bootstrap network by connecting to known peers."""
        # In production, this would connect to bootstrap servers
        # For now, implement local network discovery

        bootstrap_ports = [8003, 8004, 8005]  # Try different ports

        for port in bootstrap_ports:
            if port != self.port:
                try:
                    await self._ping_peer(f"127.0.0.1:{port}")
                except:
                    pass  # Peer not available

    async def _ping_peer(self, address: str) -> bool:
        """Ping a peer and add to routing table."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            url = f"http://{address}/p2p/ping"
            data = {
                "node_id": self.node_id,
                "address": f"127.0.0.1:{self.port}",
                "capabilities": ["surgery", "analytics", "data_sync"],
            }

            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()

                    # Add peer to routing table
                    peer = P2PPeer(
                        id=result["node_id"],
                        address=address.split(":")[0],
                        port=int(address.split(":")[1]),
                        last_seen=datetime.now(),
                        capabilities=result.get("capabilities", []),
                    )

                    self.dht.add_peer(peer)
                    logger.info(f"🤝 Connected to peer: {peer.id[:8]}... at {address}")
                    return True

        except Exception as e:
            logger.debug(f"Failed to ping peer {address}: {e}")

        return False

    async def _maintain_dht(self) -> None:
        """Periodic DHT maintenance."""
        while self.running:
            try:
                # Refresh routing table
                stale_peers = []
                current_time = datetime.now()

                for peer_id, peer in self.dht.routing_table.items():
                    if (current_time - peer.last_seen) > timedelta(minutes=5):
                        stale_peers.append(peer_id)
                    else:
                        # Ping peer to keep connection alive
                        address = f"{peer.address}:{peer.port}"
                        await self._ping_peer(address)

                # Remove stale peers
                for peer_id in stale_peers:
                    if peer_id in self.dht.routing_table:
                        del self.dht.routing_table[peer_id]

                await asyncio.sleep(60)  # Maintain every minute

            except Exception as e:
                logger.exception(f"DHT maintenance error: {e}")
                await asyncio.sleep(30)

    async def setup_torrent_style_sync(self) -> None:
        """Implement BitTorrent-style data synchronization."""
        logger.info("🔄 Setting up torrent-style data sync...")

        # Start chunk distribution service
        asyncio.create_task(self._chunk_distribution_service())

    async def _chunk_distribution_service(self) -> None:
        """Service for distributing data chunks."""
        while self.running:
            try:
                # Check for incomplete data and request missing chunks
                for data_id in self.data_chunks:
                    if not self._is_data_complete(data_id):
                        await self._request_missing_chunks(data_id)

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.exception(f"Chunk distribution error: {e}")
                await asyncio.sleep(5)

    def _is_data_complete(self, data_id: str) -> bool:
        """Check if all chunks for data are available."""
        if data_id not in self.data_chunks:
            return False

        chunks = self.data_chunks[data_id]
        if not chunks:
            return False

        # Check for consecutive chunk indices
        max_index = max(chunks.keys())
        return len(chunks) == max_index + 1

    async def _request_missing_chunks(self, data_id: str) -> None:
        """Request missing chunks from peers."""
        if data_id not in self.data_chunks:
            return

        chunks = self.data_chunks[data_id]
        max_index = max(chunks.keys()) if chunks else 0

        # Find missing chunks
        missing_chunks = []
        for i in range(max_index + 1):
            if i not in chunks:
                missing_chunks.append(i)

        # Request from peers
        for chunk_index in missing_chunks[:5]:  # Limit concurrent requests
            await self._request_chunk_from_peers(data_id, chunk_index)

    async def _request_chunk_from_peers(self, data_id: str, chunk_index: int) -> None:
        """Request specific chunk from available peers."""
        peers = list(self.dht.routing_table.values())
        random.shuffle(peers)  # Randomize peer selection

        for peer in peers[:3]:  # Try up to 3 peers
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession()

                url = f"http://{peer.address}:{peer.port}/p2p/chunk_request"
                data = {
                    "data_id": data_id,
                    "chunk_index": chunk_index,
                    "requestor": self.node_id,
                }

                async with self.session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "chunk_data" in result:
                            await self._store_received_chunk(result)
                            break

            except Exception as e:
                logger.debug(f"Failed to request chunk from peer {peer.id[:8]}: {e}")

    async def _store_received_chunk(self, chunk_data: dict) -> None:
        """Store received chunk data."""
        data_id = chunk_data["data_id"]
        chunk_index = chunk_data["chunk_index"]

        chunk = DataChunk(
            chunk_id=chunk_data["chunk_id"],
            data_id=data_id,
            index=chunk_index,
            data=chunk_data["data"].encode(),
            checksum=chunk_data["checksum"],
            size=chunk_data["size"],
        )

        # Verify chunk integrity
        calculated_checksum = hashlib.md5(chunk.data).hexdigest()
        if calculated_checksum == chunk.checksum:
            if data_id not in self.data_chunks:
                self.data_chunks[data_id] = {}
            self.data_chunks[data_id][chunk_index] = chunk
            logger.info(f"📦 Stored chunk {chunk_index} for data {data_id[:8]}...")
        else:
            logger.warning(
                f"⚠️ Chunk integrity check failed for {data_id}:{chunk_index}"
            )

    async def establish_peer_connections(self) -> None:
        """Create direct peer connections."""
        logger.info("🔗 Establishing peer connections...")

        # Use STUN/TURN for NAT traversal (simplified implementation)
        await self._setup_nat_traversal()

    async def _setup_nat_traversal(self) -> None:
        """Setup NAT traversal using STUN."""
        # Simplified NAT traversal - in production, use STUN/TURN servers
        logger.info("🌐 Setting up NAT traversal...")

    # HTTP handlers for P2P communication
    async def _handle_ping(self, request):
        """Handle ping requests from peers."""
        data = await request.json()

        # Add peer to routing table
        peer = P2PPeer(
            id=data["node_id"],
            address=request.remote,
            port=int(data["address"].split(":")[1]),
            last_seen=datetime.now(),
            capabilities=data.get("capabilities", []),
        )

        self.dht.add_peer(peer)

        return web.json_response(
            {
                "node_id": self.node_id,
                "capabilities": ["surgery", "analytics", "data_sync"],
                "status": "pong",
            }
        )

    async def _handle_find_node(self, request):
        """Handle find_node requests."""
        data = await request.json()
        target_id = data["target_id"]

        closest_peers = self.dht.find_closest_peers(target_id)

        return web.json_response({"peers": [asdict(peer) for peer in closest_peers]})

    async def _handle_store(self, request):
        """Handle store requests."""
        data = await request.json()
        key = data["key"]
        value = data["value"]

        self.dht.data_store[key] = value

        return web.json_response({"status": "stored"})

    async def _handle_find_value(self, request):
        """Handle find_value requests."""
        data = await request.json()
        key = data["key"]

        if key in self.dht.data_store:
            return web.json_response({"value": self.dht.data_store[key]})
        # Return closest peers
        closest_peers = self.dht.find_closest_peers(key)
        return web.json_response({"peers": [asdict(peer) for peer in closest_peers]})

    async def _handle_chunk_request(self, request):
        """Handle chunk requests."""
        data = await request.json()
        data_id = data["data_id"]
        chunk_index = data["chunk_index"]

        if data_id in self.data_chunks and chunk_index in self.data_chunks[data_id]:
            chunk = self.data_chunks[data_id][chunk_index]

            return web.json_response(
                {
                    "chunk_id": chunk.chunk_id,
                    "data_id": chunk.data_id,
                    "chunk_index": chunk.index,
                    "data": chunk.data.decode(),
                    "checksum": chunk.checksum,
                    "size": chunk.size,
                }
            )
        return web.json_response({"error": "Chunk not found"}, status=404)

    async def _handle_chunk_response(self, request):
        """Handle chunk responses."""
        data = await request.json()
        await self._store_received_chunk(data)
        return web.json_response({"status": "received"})

    async def store_data(self, data_id: str, data: bytes) -> None:
        """Store data in P2P network using chunking."""
        logger.info(f"📊 Storing data {data_id[:8]}... ({len(data)} bytes)")

        # Split data into chunks
        chunk_size = 64 * 1024  # 64KB chunks
        chunks = []

        for i in range(0, len(data), chunk_size):
            chunk_data = data[i : i + chunk_size]
            chunk_id = hashlib.sha1(chunk_data).hexdigest()

            chunk = DataChunk(
                chunk_id=chunk_id,
                data_id=data_id,
                index=len(chunks),
                data=chunk_data,
                checksum=hashlib.md5(chunk_data).hexdigest(),
                size=len(chunk_data),
            )

            chunks.append(chunk)

        # Store chunks locally
        self.data_chunks[data_id] = {chunk.index: chunk for chunk in chunks}

        # Distribute chunks to peers
        await self._distribute_chunks(data_id, chunks)

    async def _distribute_chunks(self, data_id: str, chunks: list[DataChunk]) -> None:
        """Distribute chunks to peer network."""
        peers = list(self.dht.routing_table.values())

        for chunk in chunks:
            # Select random peers for redundancy
            selected_peers = random.sample(peers, min(3, len(peers)))

            for peer in selected_peers:
                try:
                    await self._send_chunk_to_peer(peer, chunk)
                except Exception as e:
                    logger.debug(f"Failed to send chunk to peer {peer.id[:8]}: {e}")

    async def _send_chunk_to_peer(self, peer: P2PPeer, chunk: DataChunk) -> None:
        """Send chunk to specific peer."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"http://{peer.address}:{peer.port}/p2p/store"
        data = {
            "key": f"chunk_{chunk.data_id}_{chunk.index}",
            "value": {
                "chunk_id": chunk.chunk_id,
                "data_id": chunk.data_id,
                "chunk_index": chunk.index,
                "data": chunk.data.decode(),
                "checksum": chunk.checksum,
                "size": chunk.size,
            },
        }

        async with self.session.post(url, json=data) as response:
            if response.status == 200:
                logger.debug(f"📤 Sent chunk {chunk.index} to peer {peer.id[:8]}")

    async def retrieve_data(self, data_id: str) -> bytes | None:
        """Retrieve complete data from P2P network."""
        logger.info(f"📥 Retrieving data {data_id[:8]}...")

        # Check if we have complete data locally
        if self._is_data_complete(data_id):
            return self._assemble_data(data_id)

        # Request missing chunks from network
        await self._request_missing_chunks(data_id)

        # Wait for completion (with timeout)
        for _ in range(30):  # 30 second timeout
            if self._is_data_complete(data_id):
                return self._assemble_data(data_id)
            await asyncio.sleep(1)

        logger.warning(f"⚠️ Failed to retrieve complete data for {data_id}")
        return None

    def _assemble_data(self, data_id: str) -> bytes:
        """Assemble complete data from chunks."""
        if data_id not in self.data_chunks:
            return b""

        chunks = self.data_chunks[data_id]
        sorted_chunks = sorted(chunks.items())

        data = b""
        for _, chunk in sorted_chunks:
            data += chunk.data

        return data

    async def stop(self) -> None:
        """Stop P2P network services."""
        logger.info("🛑 Stopping P2P Network Manager...")

        self.running = False

        if self.session:
            await self.session.close()

        logger.info("✅ P2P Network Manager stopped")
