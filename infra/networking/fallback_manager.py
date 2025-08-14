"""Network Fallback Manager for graceful degradation and automatic switching
Implements fallback chain: P2P → Local → BLE → Offline.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class NetworkType(Enum):
    P2P = "p2p"
    LOCAL = "local"
    BLE_MESH = "ble_mesh"
    OFFLINE = "offline"


class NetworkStatus(Enum):
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass
class NetworkHealth:
    """Health status of a network type."""

    network_type: NetworkType
    status: NetworkStatus
    latency_ms: float
    reliability_percent: float
    bandwidth_mbps: float
    last_check: datetime
    error_count: int = 0


@dataclass
class FallbackRule:
    """Fallback rule configuration."""

    from_network: NetworkType
    to_network: NetworkType
    condition: str  # "latency_high", "connection_lost", "reliability_low"
    threshold: float
    enabled: bool = True


class NetworkFallbackManager:
    """Manages graceful network degradation and automatic switching."""

    def __init__(self) -> None:
        self.current_network = NetworkType.P2P
        self.network_health: dict[NetworkType, NetworkHealth] = {}
        self.fallback_rules: list[FallbackRule] = []
        self.is_running = False
        self.network_managers = {}
        self.offline_queue = []
        self.switching_in_progress = False

    async def start(self) -> None:
        """Start fallback manager."""
        logger.info("🔄 Starting Network Fallback Manager...")

        # Initialize network health tracking
        await self._initialize_network_health()

        # Setup fallback rules
        await self._setup_fallback_rules()

        self.is_running = True

        # Start monitoring and switching tasks
        asyncio.create_task(self._monitor_network_health())
        asyncio.create_task(self._fallback_decision_engine())
        asyncio.create_task(self._recovery_monitor())

        logger.info("✅ Network Fallback Manager started")

    async def _initialize_network_health(self) -> None:
        """Initialize network health tracking."""
        logger.info("📊 Initializing network health tracking")

        # Initialize health status for each network type
        networks = [
            NetworkType.P2P,
            NetworkType.LOCAL,
            NetworkType.BLE_MESH,
            NetworkType.OFFLINE,
        ]

        for network_type in networks:
            self.network_health[network_type] = NetworkHealth(
                network_type=network_type,
                status=NetworkStatus.UNAVAILABLE,
                latency_ms=999,
                reliability_percent=0,
                bandwidth_mbps=0,
                last_check=datetime.now(),
            )

    async def _setup_fallback_rules(self) -> None:
        """Setup network fallback rules."""
        logger.info("📋 Setting up fallback rules")

        # Define fallback chain: P2P → Local → BLE → Offline
        self.fallback_rules = [
            # P2P fallback rules
            FallbackRule(
                from_network=NetworkType.P2P,
                to_network=NetworkType.LOCAL,
                condition="latency_high",
                threshold=500,  # ms
            ),
            FallbackRule(
                from_network=NetworkType.P2P,
                to_network=NetworkType.LOCAL,
                condition="connection_lost",
                threshold=0,
            ),
            FallbackRule(
                from_network=NetworkType.P2P,
                to_network=NetworkType.LOCAL,
                condition="reliability_low",
                threshold=80,  # percent
            ),
            # Local network fallback rules
            FallbackRule(
                from_network=NetworkType.LOCAL,
                to_network=NetworkType.BLE_MESH,
                condition="connection_lost",
                threshold=0,
            ),
            FallbackRule(
                from_network=NetworkType.LOCAL,
                to_network=NetworkType.BLE_MESH,
                condition="latency_high",
                threshold=1000,  # ms
            ),
            # BLE mesh fallback rules
            FallbackRule(
                from_network=NetworkType.BLE_MESH,
                to_network=NetworkType.OFFLINE,
                condition="connection_lost",
                threshold=0,
            ),
            FallbackRule(
                from_network=NetworkType.BLE_MESH,
                to_network=NetworkType.OFFLINE,
                condition="reliability_low",
                threshold=50,  # percent
            ),
        ]

        logger.info(f"✅ Configured {len(self.fallback_rules)} fallback rules")

    async def register_network_manager(
        self, network_type: NetworkType, manager
    ) -> None:
        """Register a network manager for fallback control."""
        self.network_managers[network_type] = manager
        logger.info(f"📝 Registered {network_type.value} network manager")

    async def implement_graceful_degradation(self) -> None:
        """Implement graceful degradation across network types."""
        logger.info("⬇️ Implementing graceful degradation")

        # Start degradation monitoring
        asyncio.create_task(self._degradation_monitor())

        logger.info("✅ Graceful degradation implemented")

    async def _degradation_monitor(self) -> None:
        """Monitor for network degradation."""
        while self.is_running:
            try:
                current_health = self.network_health.get(self.current_network)

                if current_health:
                    # Check if current network is degrading
                    if current_health.status == NetworkStatus.DEGRADED:
                        logger.warning(
                            f"⚠️ Network degradation detected on {self.current_network.value}"
                        )

                        # Look for better alternatives
                        better_network = await self._find_better_network()
                        if better_network and better_network != self.current_network:
                            await self._initiate_network_switch(better_network)

                    elif current_health.status == NetworkStatus.UNAVAILABLE:
                        logger.error(
                            f"❌ Network unavailable: {self.current_network.value}"
                        )
                        await self._emergency_fallback()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Degradation monitoring error: {e}")
                await asyncio.sleep(60)

    async def _find_better_network(self) -> NetworkType | None:
        """Find a better network alternative."""
        # Score networks based on health metrics
        network_scores = {}

        for network_type, health in self.network_health.items():
            if health.status == NetworkStatus.UNAVAILABLE:
                score = 0
            else:
                # Calculate score based on latency, reliability, and bandwidth
                latency_score = max(
                    0, 100 - (health.latency_ms / 10)
                )  # Lower latency = higher score
                reliability_score = health.reliability_percent
                bandwidth_score = min(100, health.bandwidth_mbps * 10)  # Cap at 100

                score = (latency_score + reliability_score + bandwidth_score) / 3

            network_scores[network_type] = score

        # Find the best available network
        best_network = max(network_scores.keys(), key=lambda n: network_scores[n])

        # Only switch if significantly better
        current_score = network_scores.get(self.current_network, 0)
        best_score = network_scores[best_network]

        if best_score > current_score + 20:  # 20 point improvement threshold
            return best_network

        return None

    async def _emergency_fallback(self) -> None:
        """Emergency fallback when current network fails."""
        logger.warning("🚨 Emergency fallback triggered")

        # Find any available network
        for network_type in [
            NetworkType.LOCAL,
            NetworkType.BLE_MESH,
            NetworkType.OFFLINE,
        ]:
            health = self.network_health.get(network_type)
            if health and health.status != NetworkStatus.UNAVAILABLE:
                await self._initiate_network_switch(network_type)
                return

        # Last resort: go offline
        await self._initiate_network_switch(NetworkType.OFFLINE)

    async def setup_network_switching(self) -> None:
        """Setup automatic network switching."""
        logger.info("🔀 Setting up automatic network switching")

        # Start network switching engine
        asyncio.create_task(self._network_switching_engine())

        logger.info("✅ Network switching configured")

    async def _network_switching_engine(self) -> None:
        """Engine for automatic network switching."""
        while self.is_running:
            try:
                if not self.switching_in_progress:
                    # Check if we should switch networks
                    (
                        should_switch,
                        target_network,
                    ) = await self._evaluate_switch_conditions()

                    if should_switch and target_network:
                        await self._initiate_network_switch(target_network)

                await asyncio.sleep(15)  # Check every 15 seconds

            except Exception as e:
                logger.exception(f"Network switching engine error: {e}")
                await asyncio.sleep(30)

    async def _evaluate_switch_conditions(self) -> tuple[bool, NetworkType | None]:
        """Evaluate if we should switch networks."""
        current_health = self.network_health.get(self.current_network)
        if not current_health:
            return True, NetworkType.OFFLINE

        # Check fallback rules
        for rule in self.fallback_rules:
            if not rule.enabled or rule.from_network != self.current_network:
                continue

            should_trigger = False

            if rule.condition == "latency_high":
                should_trigger = current_health.latency_ms > rule.threshold
            elif rule.condition == "connection_lost":
                should_trigger = current_health.status == NetworkStatus.UNAVAILABLE
            elif rule.condition == "reliability_low":
                should_trigger = current_health.reliability_percent < rule.threshold

            if should_trigger:
                # Check if target network is available
                target_health = self.network_health.get(rule.to_network)
                if target_health and target_health.status != NetworkStatus.UNAVAILABLE:
                    return True, rule.to_network

        return False, None

    async def _initiate_network_switch(self, target_network: NetworkType) -> None:
        """Initiate switch to target network."""
        if self.switching_in_progress:
            logger.warning("Network switch already in progress")
            return

        self.switching_in_progress = True

        try:
            logger.info(
                f"🔀 Switching from {self.current_network.value} to {target_network.value}"
            )

            # Save current state
            await self._save_current_state()

            # Gracefully shutdown current network
            await self._shutdown_current_network()

            # Initialize target network
            success = await self._initialize_target_network(target_network)

            if success:
                # Update current network
                old_network = self.current_network
                self.current_network = target_network

                # Restore state on new network
                await self._restore_state_on_new_network()

                logger.info(f"✅ Successfully switched to {target_network.value}")

                # Log the switch
                await self._log_network_switch(old_network, target_network, "success")

            else:
                logger.error(f"❌ Failed to initialize {target_network.value}")
                await self._log_network_switch(
                    self.current_network, target_network, "failed"
                )

        except Exception as e:
            logger.exception(f"Network switch error: {e}")
            await self._log_network_switch(
                self.current_network, target_network, "error"
            )

        finally:
            self.switching_in_progress = False

    async def _save_current_state(self) -> None:
        """Save current network state for restoration."""
        logger.debug("💾 Saving current network state")

        # This would save current collaboration state, pending operations, etc.
        current_state = {
            "timestamp": datetime.now().isoformat(),
            "network": self.current_network.value,
            "pending_operations": len(self.offline_queue),
            "active_sessions": 3,  # Would get from collaboration engine
        }

        # Store state for restoration
        self.saved_state = current_state

    async def _shutdown_current_network(self) -> None:
        """Gracefully shutdown current network."""
        logger.debug(f"⏹️ Shutting down {self.current_network.value} network")

        current_manager = self.network_managers.get(self.current_network)
        if current_manager and hasattr(current_manager, "stop"):
            try:
                await current_manager.stop()
            except Exception as e:
                logger.exception(f"Error stopping {self.current_network.value}: {e}")

    async def _initialize_target_network(self, target_network: NetworkType) -> bool:
        """Initialize target network."""
        logger.debug(f"🚀 Initializing {target_network.value} network")

        try:
            target_manager = self.network_managers.get(target_network)

            if target_network == NetworkType.OFFLINE:
                # Offline mode doesn't need initialization
                return True
            if target_manager and hasattr(target_manager, "start"):
                await target_manager.start()
                return True
            logger.warning(f"No manager available for {target_network.value}")
            return False

        except Exception as e:
            logger.exception(f"Failed to initialize {target_network.value}: {e}")
            return False

    async def _restore_state_on_new_network(self) -> None:
        """Restore saved state on new network."""
        logger.debug(f"🔄 Restoring state on {self.current_network.value}")

        # This would restore collaboration sessions, sync queued operations, etc.
        if hasattr(self, "saved_state"):
            logger.info(f"🔄 Restored state from {self.saved_state['network']}")

    async def _log_network_switch(
        self, from_network: NetworkType, to_network: NetworkType, result: str
    ) -> None:
        """Log network switch event."""
        switch_event = {
            "timestamp": datetime.now().isoformat(),
            "from_network": from_network.value,
            "to_network": to_network.value,
            "result": result,
            "switching_time_ms": 1000,  # Would measure actual time
        }

        logger.info(f"📝 Network switch logged: {switch_event}")

    async def implement_data_recovery(self) -> None:
        """Implement data recovery from network partitions."""
        logger.info("🛟 Implementing data recovery mechanisms")

        # Start data recovery monitoring
        asyncio.create_task(self._data_recovery_monitor())

        logger.info("✅ Data recovery implemented")

    async def _data_recovery_monitor(self) -> None:
        """Monitor and handle data recovery."""
        while self.is_running:
            try:
                # Check for network partitions
                partition_detected = await self._detect_network_partition()

                if partition_detected:
                    logger.warning("🔍 Network partition detected")
                    await self._handle_network_partition()

                # Process offline queue when connected
                if self.current_network != NetworkType.OFFLINE and self.offline_queue:
                    await self._process_offline_queue()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.exception(f"Data recovery monitoring error: {e}")
                await asyncio.sleep(120)

    async def _detect_network_partition(self) -> bool:
        """Detect if we're in a network partition."""
        # Check if we can reach any other nodes
        reachable_nodes = 0

        for health in self.network_health.values():
            if health.status == NetworkStatus.AVAILABLE:
                reachable_nodes += 1

        # If we can only reach ourselves, we might be partitioned
        return reachable_nodes <= 1

    async def _handle_network_partition(self) -> None:
        """Handle network partition scenario."""
        logger.warning("🔧 Handling network partition")

        # Switch to best available network or offline mode
        best_network = await self._find_best_available_network()

        if best_network and best_network != self.current_network:
            await self._initiate_network_switch(best_network)
        elif best_network is None:
            await self._initiate_network_switch(NetworkType.OFFLINE)

    async def _find_best_available_network(self) -> NetworkType | None:
        """Find the best available network during partition."""
        available_networks = [
            network_type
            for network_type, health in self.network_health.items()
            if health.status == NetworkStatus.AVAILABLE
        ]

        if not available_networks:
            return None

        # Prefer order: P2P > Local > BLE > Offline
        preference_order = [
            NetworkType.P2P,
            NetworkType.LOCAL,
            NetworkType.BLE_MESH,
            NetworkType.OFFLINE,
        ]

        for preferred in preference_order:
            if preferred in available_networks:
                return preferred

        return available_networks[0]

    async def _process_offline_queue(self) -> None:
        """Process queued operations when back online."""
        if not self.offline_queue:
            return

        logger.info(f"🔄 Processing {len(self.offline_queue)} offline operations")

        try:
            # Process operations in batches
            batch_size = 10
            while self.offline_queue:
                batch = self.offline_queue[:batch_size]
                self.offline_queue = self.offline_queue[batch_size:]

                for operation in batch:
                    await self._process_offline_operation(operation)

                # Small delay between batches
                await asyncio.sleep(0.1)

            logger.info("✅ Offline queue processed successfully")

        except Exception as e:
            logger.exception(f"Error processing offline queue: {e}")

    async def _process_offline_operation(self, operation: dict) -> None:
        """Process a single offline operation."""
        try:
            # This would integrate with the appropriate manager to process the operation
            logger.debug(
                f"Processing offline operation: {operation.get('type', 'unknown')}"
            )

        except Exception as e:
            logger.exception(f"Failed to process offline operation: {e}")

    async def _monitor_network_health(self) -> None:
        """Monitor health of all networks."""
        while self.is_running:
            try:
                for network_type in self.network_health:
                    await self._check_network_health(network_type)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Network health monitoring error: {e}")
                await asyncio.sleep(60)

    async def _check_network_health(self, network_type: NetworkType) -> None:
        """Check health of specific network type."""
        try:
            health = self.network_health[network_type]

            # Simulate health check (would be real network tests)
            if network_type == NetworkType.OFFLINE:
                # Offline is always "available" but with zero performance
                health.status = NetworkStatus.AVAILABLE
                health.latency_ms = 0
                health.reliability_percent = 100
                health.bandwidth_mbps = 0
            else:
                # Simulate network check
                manager = self.network_managers.get(network_type)
                if manager:
                    # Would get real metrics from manager
                    health.latency_ms = 50 + (hash(str(datetime.now())) % 100)
                    health.reliability_percent = 90 + (hash(str(datetime.now())) % 10)
                    health.bandwidth_mbps = 10 + (hash(str(datetime.now())) % 20)
                    health.status = NetworkStatus.AVAILABLE
                else:
                    health.status = NetworkStatus.UNAVAILABLE

            health.last_check = datetime.now()

        except Exception as e:
            logger.exception(f"Health check failed for {network_type.value}: {e}")
            self.network_health[network_type].status = NetworkStatus.UNAVAILABLE

    async def _fallback_decision_engine(self) -> None:
        """Engine for making fallback decisions."""
        while self.is_running:
            try:
                # Evaluate current network performance
                current_health = self.network_health.get(self.current_network)

                if (
                    current_health
                    and current_health.status == NetworkStatus.UNAVAILABLE
                ):
                    logger.warning(
                        f"⚠️ Current network {self.current_network.value} unavailable"
                    )

                    # Find fallback option
                    fallback_network = await self._find_fallback_network()
                    if fallback_network:
                        await self._initiate_network_switch(fallback_network)

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.exception(f"Fallback decision engine error: {e}")
                await asyncio.sleep(30)

    async def _find_fallback_network(self) -> NetworkType | None:
        """Find appropriate fallback network."""
        # Check fallback rules for current network
        for rule in self.fallback_rules:
            if rule.enabled and rule.from_network == self.current_network:
                target_health = self.network_health.get(rule.to_network)
                if target_health and target_health.status != NetworkStatus.UNAVAILABLE:
                    return rule.to_network

        return None

    async def _recovery_monitor(self) -> None:
        """Monitor for network recovery opportunities."""
        while self.is_running:
            try:
                # Check if we can recover to a better network
                if self.current_network != NetworkType.P2P:
                    # Always try to recover to P2P if available
                    p2p_health = self.network_health.get(NetworkType.P2P)
                    if p2p_health and p2p_health.status == NetworkStatus.AVAILABLE:
                        logger.info("🔄 P2P network recovered - attempting switch")
                        await self._initiate_network_switch(NetworkType.P2P)

                await asyncio.sleep(120)  # Check every 2 minutes

            except Exception as e:
                logger.exception(f"Recovery monitoring error: {e}")
                await asyncio.sleep(300)

    async def add_to_offline_queue(self, operation: dict) -> None:
        """Add operation to offline queue."""
        operation["queued_at"] = datetime.now().isoformat()
        self.offline_queue.append(operation)
        logger.debug(
            f"📝 Added operation to offline queue: {operation.get('type', 'unknown')}"
        )

    async def get_fallback_status(self) -> dict:
        """Get fallback manager status."""
        return {
            "active": self.is_running,
            "current_network": self.current_network.value,
            "switching_in_progress": self.switching_in_progress,
            "offline_queue_size": len(self.offline_queue),
            "network_health": {
                network_type.value: {
                    "status": health.status.value,
                    "latency_ms": health.latency_ms,
                    "reliability_percent": health.reliability_percent,
                    "bandwidth_mbps": health.bandwidth_mbps,
                    "last_check": health.last_check.isoformat(),
                    "error_count": health.error_count,
                }
                for network_type, health in self.network_health.items()
            },
            "fallback_rules": [
                {
                    "from": rule.from_network.value,
                    "to": rule.to_network.value,
                    "condition": rule.condition,
                    "threshold": rule.threshold,
                    "enabled": rule.enabled,
                }
                for rule in self.fallback_rules
            ],
        }

    async def stop(self) -> None:
        """Stop fallback manager."""
        logger.info("🛑 Stopping Network Fallback Manager")
        self.is_running = False
