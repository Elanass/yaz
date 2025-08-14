"""Network Monitor for comprehensive network health and performance tracking
Monitors all network types: local, P2P, BLE mesh, and multi-VM.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime

import aiohttp
import psutil


logger = logging.getLogger(__name__)


@dataclass
class NetworkMetrics:
    """Network performance metrics."""

    latency_ms: float
    bandwidth_mbps: float
    packet_loss_percent: float
    jitter_ms: float
    connection_count: int
    timestamp: datetime


@dataclass
class NodeHealth:
    """Health status of a network node."""

    node_id: str
    node_type: str  # local, p2p, ble, vm
    status: str  # healthy, warning, critical, offline
    last_seen: datetime
    metrics: NetworkMetrics
    errors: list[str]


class NetworkMonitor:
    """Monitors network health and performance across all network types."""

    def __init__(self) -> None:
        self.is_running = False
        self.node_health: dict[str, NodeHealth] = {}
        self.network_metrics_history: list[NetworkMetrics] = []
        self.alerts: list[dict] = []
        self.performance_thresholds = {
            "latency_warning": 100,  # ms
            "latency_critical": 500,  # ms
            "packet_loss_warning": 1,  # %
            "packet_loss_critical": 5,  # %
            "bandwidth_warning": 10,  # Mbps
            "bandwidth_critical": 1,  # Mbps
        }

    async def start(self) -> None:
        """Start network monitoring."""
        logger.info("📊 Starting Network Monitor...")

        self.is_running = True

        # Start monitoring tasks
        asyncio.create_task(self._monitor_local_network())
        asyncio.create_task(self._monitor_p2p_network())
        asyncio.create_task(self._monitor_ble_mesh())
        asyncio.create_task(self._monitor_vm_cluster())
        asyncio.create_task(self._monitor_system_resources())
        asyncio.create_task(self._analyze_network_health())
        asyncio.create_task(self._alert_manager())

        logger.info("✅ Network Monitor started")

    async def monitor_connection_health(self) -> None:
        """Track connection quality across all network types."""
        logger.info("🔍 Monitoring connection health across all networks")

        # Start comprehensive monitoring
        asyncio.create_task(self._comprehensive_health_check())

    async def _monitor_local_network(self) -> None:
        """Monitor local network performance."""
        while self.is_running:
            try:
                # Get local network interface stats
                psutil.net_io_counters()

                # Calculate metrics
                await self._calculate_local_metrics()

                # Check local peers health
                await self._check_local_peers_health()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Local network monitoring error: {e}")
                await asyncio.sleep(60)

    async def _calculate_local_metrics(self) -> NetworkMetrics:
        """Calculate local network metrics."""
        try:
            # Ping localhost to measure basic latency
            start_time = time.time()

            # Simple connectivity test
            try:
                import socket

                s = socket.create_connection(("127.0.0.1", 80), timeout=1)
                s.close()
                latency = (time.time() - start_time) * 1000
            except:
                latency = 999  # High latency if can't connect

            # Get network interface stats for bandwidth estimation
            net_stats = psutil.net_io_counters()

            # Estimate bandwidth (simplified)
            bandwidth_mbps = (
                (net_stats.bytes_sent + net_stats.bytes_recv) / (1024 * 1024) / 60
            )  # MB/min to Mbps

            return NetworkMetrics(
                latency_ms=latency,
                bandwidth_mbps=min(bandwidth_mbps, 1000),  # Cap at 1 Gbps
                packet_loss_percent=0,  # Would need more sophisticated measurement
                jitter_ms=latency * 0.1,  # Estimate jitter as 10% of latency
                connection_count=len(psutil.net_connections()),
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.exception(f"Failed to calculate local metrics: {e}")
            return NetworkMetrics(
                latency_ms=999,
                bandwidth_mbps=0,
                packet_loss_percent=100,
                jitter_ms=999,
                connection_count=0,
                timestamp=datetime.now(),
            )

    async def _check_local_peers_health(self) -> None:
        """Check health of local network peers."""
        # This would integrate with LocalNetworkManager
        local_peers = []  # Would get from LocalNetworkManager

        for peer in local_peers:
            try:
                # Test peer connectivity
                is_healthy = await self._ping_peer(peer.get("ip"), peer.get("port"))

                if is_healthy:
                    status = "healthy"
                    errors = []
                else:
                    status = "critical"
                    errors = ["Connection failed"]

                # Update node health
                node_health = NodeHealth(
                    node_id=peer.get("id", "unknown"),
                    node_type="local",
                    status=status,
                    last_seen=datetime.now(),
                    metrics=await self._calculate_local_metrics(),
                    errors=errors,
                )

                self.node_health[peer.get("id", "unknown")] = node_health

            except Exception as e:
                logger.exception(f"Peer health check failed: {e}")

    async def _ping_peer(self, ip: str, port: int) -> bool:
        """Ping a network peer."""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(f"http://{ip}:{port}/health") as response:
                    return response.status == 200
        except Exception:
            return False

    async def _monitor_p2p_network(self) -> None:
        """Monitor P2P network performance."""
        while self.is_running:
            try:
                # This would integrate with P2PNetworkManager
                await self._calculate_p2p_metrics()

                # Check P2P peer health
                await self._check_p2p_peers_health()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.exception(f"P2P network monitoring error: {e}")
                await asyncio.sleep(120)

    async def _calculate_p2p_metrics(self) -> NetworkMetrics:
        """Calculate P2P network metrics."""
        # Simulate P2P metrics
        return NetworkMetrics(
            latency_ms=50 + (time.time() % 10),  # Simulate variable latency
            bandwidth_mbps=20 + (time.time() % 5),
            packet_loss_percent=0.1,
            jitter_ms=5,
            connection_count=3,  # Simulate 3 P2P connections
            timestamp=datetime.now(),
        )

    async def _check_p2p_peers_health(self) -> None:
        """Check health of P2P peers."""
        # Simulate P2P peer health checks
        simulated_peers = [
            {"id": "p2p_peer_1", "status": "healthy"},
            {"id": "p2p_peer_2", "status": "healthy"},
            {"id": "p2p_peer_3", "status": "warning"},
        ]

        for peer in simulated_peers:
            node_health = NodeHealth(
                node_id=peer["id"],
                node_type="p2p",
                status=peer["status"],
                last_seen=datetime.now(),
                metrics=await self._calculate_p2p_metrics(),
                errors=["High latency"] if peer["status"] == "warning" else [],
            )

            self.node_health[peer["id"]] = node_health

    async def _monitor_ble_mesh(self) -> None:
        """Monitor BLE mesh network."""
        while self.is_running:
            try:
                # This would integrate with BLEMeshManager
                await self._calculate_ble_metrics()

                # Check BLE peer health
                await self._check_ble_peers_health()

                await asyncio.sleep(45)  # Check every 45 seconds

            except Exception as e:
                logger.exception(f"BLE mesh monitoring error: {e}")
                await asyncio.sleep(90)

    async def _calculate_ble_metrics(self) -> NetworkMetrics:
        """Calculate BLE mesh metrics."""
        # Simulate BLE metrics (lower performance than WiFi/Ethernet)
        return NetworkMetrics(
            latency_ms=200 + (time.time() % 50),  # Higher latency for BLE
            bandwidth_mbps=0.1 + (time.time() % 0.05),  # Very low bandwidth
            packet_loss_percent=2 + (time.time() % 3),  # Higher packet loss
            jitter_ms=20 + (time.time() % 10),
            connection_count=2,  # Simulate 2 BLE connections
            timestamp=datetime.now(),
        )

    async def _check_ble_peers_health(self) -> None:
        """Check health of BLE mesh peers."""
        # Simulate BLE peer health
        simulated_ble_peers = [
            {"id": "ble_device_1", "rssi": -45, "status": "healthy"},
            {"id": "ble_device_2", "rssi": -65, "status": "warning"},
        ]

        for peer in simulated_ble_peers:
            status = "healthy" if peer["rssi"] > -60 else "warning"
            errors = ["Weak signal"] if peer["rssi"] < -60 else []

            node_health = NodeHealth(
                node_id=peer["id"],
                node_type="ble",
                status=status,
                last_seen=datetime.now(),
                metrics=await self._calculate_ble_metrics(),
                errors=errors,
            )

            self.node_health[peer["id"]] = node_health

    async def _monitor_vm_cluster(self) -> None:
        """Monitor VM cluster health."""
        while self.is_running:
            try:
                # This would integrate with MultiVMManager
                await self._calculate_vm_metrics()

                # Check VM health
                await self._check_vm_health()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"VM cluster monitoring error: {e}")
                await asyncio.sleep(60)

    async def _calculate_vm_metrics(self) -> NetworkMetrics:
        """Calculate VM cluster metrics."""
        return NetworkMetrics(
            latency_ms=10 + (time.time() % 5),  # Low latency within cluster
            bandwidth_mbps=100 + (time.time() % 20),  # High bandwidth
            packet_loss_percent=0.01,  # Very low packet loss
            jitter_ms=1 + (time.time() % 2),
            connection_count=5,  # Simulate 5 VM connections
            timestamp=datetime.now(),
        )

    async def _check_vm_health(self) -> None:
        """Check health of VMs in cluster."""
        # Simulate VM health checks
        simulated_vms = [
            {"id": "vm_01", "ip": "10.0.1.10", "status": "healthy"},
            {"id": "vm_02", "ip": "10.0.1.11", "status": "healthy"},
            {"id": "vm_03", "ip": "10.0.1.12", "status": "healthy"},
        ]

        for vm in simulated_vms:
            # Simulate health check
            is_healthy = await self._ping_peer(vm["ip"], 8000)
            status = "healthy" if is_healthy else "critical"
            errors = [] if is_healthy else ["VM unreachable"]

            node_health = NodeHealth(
                node_id=vm["id"],
                node_type="vm",
                status=status,
                last_seen=datetime.now(),
                metrics=await self._calculate_vm_metrics(),
                errors=errors,
            )

            self.node_health[vm["id"]] = node_health

    async def _monitor_system_resources(self) -> None:
        """Monitor system resource usage."""
        while self.is_running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)

                # Memory usage
                memory = psutil.virtual_memory()

                # Disk usage
                disk = psutil.disk_usage("/")

                # Network I/O
                psutil.net_io_counters()

                # Log resource usage
                logger.debug(
                    f"💻 System Resources - CPU: {cpu_percent}%, "
                    f"Memory: {memory.percent}%, Disk: {disk.percent}%"
                )

                # Check for resource alerts
                if cpu_percent > 80:
                    await self._create_alert("high_cpu", f"CPU usage: {cpu_percent}%")

                if memory.percent > 85:
                    await self._create_alert(
                        "high_memory", f"Memory usage: {memory.percent}%"
                    )

                if disk.percent > 90:
                    await self._create_alert(
                        "high_disk", f"Disk usage: {disk.percent}%"
                    )

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"System resource monitoring error: {e}")
                await asyncio.sleep(60)

    async def measure_sync_performance(self) -> None:
        """Monitor data synchronization performance."""
        logger.info("⏱️ Measuring sync performance")

        # Start sync performance monitoring
        asyncio.create_task(self._sync_performance_monitor())

    async def _sync_performance_monitor(self) -> None:
        """Monitor synchronization performance."""
        while self.is_running:
            try:
                # This would integrate with SyncEngine
                sync_stats = {
                    "sync_operations_per_minute": 10 + (time.time() % 5),
                    "average_sync_time_ms": 100 + (time.time() % 50),
                    "failed_syncs": 0,
                    "conflict_resolution_time_ms": 200 + (time.time() % 100),
                }

                logger.debug(f"🔄 Sync Performance: {sync_stats}")

                # Check for sync performance issues
                if sync_stats["average_sync_time_ms"] > 500:
                    await self._create_alert(
                        "slow_sync",
                        f"Slow sync: {sync_stats['average_sync_time_ms']}ms",
                    )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.exception(f"Sync performance monitoring error: {e}")
                await asyncio.sleep(120)

    async def track_collaboration_metrics(self) -> None:
        """Measure team collaboration effectiveness."""
        logger.info("👥 Tracking collaboration metrics")

        # Start collaboration metrics tracking
        asyncio.create_task(self._collaboration_metrics_monitor())

    async def _collaboration_metrics_monitor(self) -> None:
        """Monitor collaboration effectiveness."""
        while self.is_running:
            try:
                # This would integrate with CollaborationEngine
                collab_stats = {
                    "active_users": 3 + int(time.time() % 5),
                    "concurrent_sessions": 2 + int(time.time() % 3),
                    "operations_per_minute": 20 + int(time.time() % 10),
                    "conflict_rate_percent": 1 + (time.time() % 2),
                    "average_response_time_ms": 50 + (time.time() % 25),
                }

                logger.debug(f"🤝 Collaboration: {collab_stats}")

                # Check collaboration health
                if collab_stats["conflict_rate_percent"] > 5:
                    await self._create_alert(
                        "high_conflicts",
                        f"High conflict rate: {collab_stats['conflict_rate_percent']}%",
                    )

                await asyncio.sleep(120)  # Check every 2 minutes

            except Exception as e:
                logger.exception(f"Collaboration metrics error: {e}")
                await asyncio.sleep(240)

    async def _analyze_network_health(self) -> None:
        """Analyze overall network health."""
        while self.is_running:
            try:
                # Collect current metrics
                datetime.now()

                # Calculate overall health score
                health_score = await self._calculate_health_score()

                # Store metrics history
                if self.network_metrics_history:
                    latest_metrics = self.network_metrics_history[-1]
                    self.network_metrics_history.append(latest_metrics)

                # Keep only last 1000 entries
                if len(self.network_metrics_history) > 1000:
                    self.network_metrics_history = self.network_metrics_history[-500:]

                logger.debug(f"📊 Network Health Score: {health_score}/100")

                await asyncio.sleep(300)  # Analyze every 5 minutes

            except Exception as e:
                logger.exception(f"Network health analysis error: {e}")
                await asyncio.sleep(600)

    async def _calculate_health_score(self) -> float:
        """Calculate overall network health score (0-100)."""
        try:
            if not self.node_health:
                return 50  # Neutral score if no data

            total_score = 0
            node_count = len(self.node_health)

            for node_health in self.node_health.values():
                node_score = 100  # Start with perfect score

                # Deduct points based on status
                if node_health.status == "warning":
                    node_score -= 25
                elif node_health.status == "critical":
                    node_score -= 50
                elif node_health.status == "offline":
                    node_score -= 100

                # Deduct points for high latency
                if (
                    node_health.metrics.latency_ms
                    > self.performance_thresholds["latency_warning"]
                ):
                    node_score -= 10
                if (
                    node_health.metrics.latency_ms
                    > self.performance_thresholds["latency_critical"]
                ):
                    node_score -= 20

                # Deduct points for packet loss
                if (
                    node_health.metrics.packet_loss_percent
                    > self.performance_thresholds["packet_loss_warning"]
                ):
                    node_score -= 10
                if (
                    node_health.metrics.packet_loss_percent
                    > self.performance_thresholds["packet_loss_critical"]
                ):
                    node_score -= 20

                total_score += max(0, node_score)  # Ensure non-negative

            return total_score / node_count if node_count > 0 else 50

        except Exception as e:
            logger.exception(f"Health score calculation error: {e}")
            return 50

    async def _alert_manager(self) -> None:
        """Manage network alerts."""
        while self.is_running:
            try:
                # Process pending alerts
                if self.alerts:
                    recent_alerts = [
                        a
                        for a in self.alerts
                        if (datetime.now() - a["timestamp"]).total_seconds() < 3600
                    ]

                    if recent_alerts:
                        logger.info(f"🚨 {len(recent_alerts)} active alerts")

                    # Clean up old alerts
                    self.alerts = recent_alerts

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.exception(f"Alert management error: {e}")
                await asyncio.sleep(120)

    async def _create_alert(self, alert_type: str, message: str) -> None:
        """Create a network alert."""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now(),
            "severity": "warning",  # Could be determined based on alert_type
        }

        self.alerts.append(alert)
        logger.warning(f"🚨 Alert: {alert_type} - {message}")

    async def _comprehensive_health_check(self) -> None:
        """Perform comprehensive health check across all networks."""
        while self.is_running:
            try:
                logger.info("🔍 Performing comprehensive health check")

                # Check all network types
                health_summary = {
                    "local_network": len(
                        [
                            n
                            for n in self.node_health.values()
                            if n.node_type == "local" and n.status == "healthy"
                        ]
                    ),
                    "p2p_network": len(
                        [
                            n
                            for n in self.node_health.values()
                            if n.node_type == "p2p" and n.status == "healthy"
                        ]
                    ),
                    "ble_mesh": len(
                        [
                            n
                            for n in self.node_health.values()
                            if n.node_type == "ble" and n.status == "healthy"
                        ]
                    ),
                    "vm_cluster": len(
                        [
                            n
                            for n in self.node_health.values()
                            if n.node_type == "vm" and n.status == "healthy"
                        ]
                    ),
                }

                logger.info(f"🏥 Network Health Summary: {health_summary}")

                await asyncio.sleep(600)  # Comprehensive check every 10 minutes

            except Exception as e:
                logger.exception(f"Comprehensive health check error: {e}")
                await asyncio.sleep(1200)

    async def get_network_status(self) -> dict:
        """Get comprehensive network status."""
        health_score = await self._calculate_health_score()

        return {
            "overall_health_score": health_score,
            "total_nodes": len(self.node_health),
            "healthy_nodes": len(
                [n for n in self.node_health.values() if n.status == "healthy"]
            ),
            "warning_nodes": len(
                [n for n in self.node_health.values() if n.status == "warning"]
            ),
            "critical_nodes": len(
                [n for n in self.node_health.values() if n.status == "critical"]
            ),
            "offline_nodes": len(
                [n for n in self.node_health.values() if n.status == "offline"]
            ),
            "active_alerts": len(self.alerts),
            "network_types": {
                "local": len(
                    [n for n in self.node_health.values() if n.node_type == "local"]
                ),
                "p2p": len(
                    [n for n in self.node_health.values() if n.node_type == "p2p"]
                ),
                "ble": len(
                    [n for n in self.node_health.values() if n.node_type == "ble"]
                ),
                "vm": len(
                    [n for n in self.node_health.values() if n.node_type == "vm"]
                ),
            },
            "performance_thresholds": self.performance_thresholds,
            "monitoring_active": self.is_running,
        }

    async def stop(self) -> None:
        """Stop network monitor."""
        logger.info("🛑 Stopping Network Monitor")
        self.is_running = False
