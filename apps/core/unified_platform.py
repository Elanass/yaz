"""Unified Yaz Healthcare Platform
Main application entry point that coordinates all components.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("yaz-unified-platform")


class UnifiedYazPlatform:
    """Unified Yaz Healthcare Platform with networking capabilities."""

    def __init__(self) -> None:
        self.app = None
        self.networking_enabled = False
        self.collaboration_engine = None
        self.apps_loaded = {}

        # Setup paths
        self.root_path = Path(__file__).parent.parent  # /workspaces/yaz
        self.src_path = self.root_path / "src"
        self.apps_path = self.root_path / "apps"

        # Add to Python path
        for path in [self.src_path, self.apps_path]:
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))

    async def create_app(
        self,
        enable_networking: bool = True,
        enable_p2p: bool = True,
        enable_ble_mesh: bool = True,
        enable_multi_vm: bool = True,
        apps_to_load: list | None = None,
    ) -> FastAPI:
        """Create unified platform application."""
        logger.info("🚀 Creating Unified Yaz Healthcare Platform...")

        # Create main FastAPI application
        self.app = FastAPI(
            title="Yaz Healthcare Platform - Unified",
            description="Advanced healthcare platform with multi-domain collaboration and networking",
            version="4.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc",
            openapi_tags=[
                {"name": "Platform", "description": "Core platform services"},
                {"name": "Dashboard", "description": "Unified dashboard and analytics"},
                {
                    "name": "Surgery",
                    "description": "Surge - Advanced surgical analytics",
                },
                {"name": "Clinical", "description": "Clinica - Clinical operations"},
                {"name": "Education", "description": "Educa - Medical education"},
                {"name": "Insurance", "description": "Insura - Insurance management"},
                {"name": "Logistics", "description": "Move - Healthcare logistics"},
                {
                    "name": "Networking",
                    "description": "Advanced networking and collaboration",
                },
                {
                    "name": "Collaboration",
                    "description": "Real-time team collaboration",
                },
            ],
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Initialize networking if enabled
        if enable_networking:
            await self._initialize_networking(
                enable_p2p, enable_ble_mesh, enable_multi_vm
            )

        # Load and integrate applications
        await self._load_applications(
            apps_to_load or ["surge", "clinica", "educa", "insura", "move"]
        )

        # Setup static files and dashboard
        await self._setup_static_files()
        await self._setup_dashboard()

        # Add core routes
        await self._add_core_routes()

        logger.info("✅ Unified Yaz Healthcare Platform created successfully")
        return self.app

    async def _initialize_networking(
        self, enable_p2p, enable_ble_mesh, enable_multi_vm
    ) -> None:
        """Initialize advanced networking capabilities."""
        logger.info("🌐 Initializing advanced networking...")

        try:
            # Import networking components
            from shared.networking.collaboration_engine import CollaborationEngine
            from shared.networking.local_network import LocalNetworkManager
            from shared.networking.p2p_network import P2PNetworkManager

            # Initialize local network
            self.local_network = LocalNetworkManager(port=8001)
            await self.local_network.start()
            logger.info("✅ Local network initialized")

            # Initialize P2P if enabled
            if enable_p2p:
                self.p2p_network = P2PNetworkManager(port=8003)
                await self.p2p_network.initialize_dht()
                logger.info("✅ P2P network initialized")

            # Initialize collaboration engine
            self.collaboration_engine = CollaborationEngine()
            await self.collaboration_engine.start()
            logger.info("✅ Collaboration engine started")

            self.networking_enabled = True

        except Exception as e:
            logger.warning(f"⚠️ Networking initialization failed: {e}")
            logger.info("📱 Platform will run in single-node mode")

    async def _load_applications(self, apps_to_load) -> None:
        """Load and integrate healthcare applications."""
        logger.info(f"📦 Loading applications: {apps_to_load}")

        # Load Surge first (primary platform)
        if "surge" in apps_to_load:
            await self._load_surge_platform()

        # Load other medical modules
        for app_name in apps_to_load:
            if app_name != "surge":  # Surge already loaded
                await self._load_medical_module(app_name)

    async def _load_surge_platform(self) -> None:
        """Load the core Surge platform."""
        try:
            # Import Surge core platform with proper path
            surge_path = str(self.src_path / "surge")
            if surge_path not in sys.path:
                sys.path.insert(0, surge_path)

            # Try different import paths for the Surge web router
            try:
                from ui.web.router import web_router as surge_web_router
            except ImportError:
                # Need to load all dependencies first due to relative imports
                try:
                    # Load pages modules first
                    pages_path = self.src_path / "surge" / "ui" / "web" / "pages"
                    sys.path.insert(0, str(pages_path))

                    # Import modules that router depends on
                    import importlib.util

                    # Load auth, dashboard, home modules
                    for module_name in ["auth", "dashboard", "home"]:
                        module_path = pages_path / f"{module_name}.py"
                        if module_path.exists():
                            spec = importlib.util.spec_from_file_location(
                                module_name, module_path
                            )
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[module_name] = module
                            spec.loader.exec_module(module)

                    # Now load the router
                    router_path = self.src_path / "surge" / "ui" / "web" / "router.py"
                    spec = importlib.util.spec_from_file_location("router", router_path)
                    router_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(router_module)
                    surge_web_router = router_module.web_router
                except Exception as e:
                    msg = f"Could not load Surge web router: {e}"
                    raise ImportError(msg)

            # Include Surge web router at root
            self.app.include_router(surge_web_router, tags=["Surgery", "Platform"])

            # Try to load Surge API
            try:
                import importlib.util

                api_router_path = self.src_path / "surge" / "api" / "router.py"
                if api_router_path.exists():
                    spec = importlib.util.spec_from_file_location(
                        "api_router", api_router_path
                    )
                    api_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(api_module)
                    surge_api_router = api_module.api_router
                    self.app.include_router(
                        surge_api_router,
                        prefix="/api",
                        tags=["Surgery", "AI", "Analytics"],
                    )
                else:
                    logger.warning("⚠️ Surge API router not found")
            except Exception as api_e:
                logger.warning(f"⚠️ Surge API services not available: {api_e}")

            self.apps_loaded["surge"] = {
                "name": "Surge",
                "description": "Advanced surgical analytics",
                "prefix": "",
                "tags": ["Surgery", "Analytics"],
            }
            logger.info("✅ Surge Platform loaded")

        except Exception as e:
            logger.exception(f"❌ Failed to load Surge platform: {e}")
            msg = f"Cannot start platform without Surge: {e}"
            raise RuntimeError(msg)

    async def _load_medical_module(self, app_name) -> None:
        """Load a medical module."""
        app_configs = {
            "clinica": {
                "name": "Clinica",
                "description": "Clinical operations",
                "prefix": "/clinica",
                "tags": ["Clinical"],
            },
            "educa": {
                "name": "Educa",
                "description": "Medical education",
                "prefix": "/educa",
                "tags": ["Education"],
            },
            "insura": {
                "name": "Insura",
                "description": "Insurance management",
                "prefix": "/insura",
                "tags": ["Insurance"],
            },
            "move": {
                "name": "Move",
                "description": "Healthcare logistics",
                "prefix": "/move",
                "tags": ["Logistics"],
            },
        }

        if app_name not in app_configs:
            logger.warning(f"⚠️ Unknown app: {app_name}")
            return

        try:
            config = app_configs[app_name]
            module = __import__(f"{app_name}.router", fromlist=["router"])

            self.app.include_router(
                module.router, prefix=config["prefix"], tags=config["tags"]
            )

            self.apps_loaded[app_name] = config
            logger.info(f"✅ {config['name']} loaded successfully")

        except Exception as e:
            logger.warning(f"⚠️ Failed to load {app_configs[app_name]['name']}: {e}")

    async def _setup_static_files(self) -> None:
        """Setup static file serving."""
        # Try Surge static files first
        surge_static_dir = self.src_path / "surge" / "ui" / "web" / "static"
        if surge_static_dir.exists():
            self.app.mount(
                "/static", StaticFiles(directory=str(surge_static_dir)), name="static"
            )
            self.app.mount(
                "/css", StaticFiles(directory=str(surge_static_dir / "css")), name="css"
            )
            self.app.mount(
                "/js", StaticFiles(directory=str(surge_static_dir / "js")), name="js"
            )
            logger.info("✅ Static files mounted from Surge")
        else:
            # Fallback static directory
            static_dir = self.root_path / "static"
            if static_dir.exists():
                self.app.mount(
                    "/static", StaticFiles(directory=str(static_dir)), name="static"
                )

    async def _setup_dashboard(self) -> None:
        """Setup unified dashboard."""
        try:
            # Check if dashboard exists in surge UI
            dashboard_path = self.src_path / "surge" / "ui" / "web" / "dashboard"
            if dashboard_path.exists():
                # Import dashboard router using importlib to avoid relative import issues
                import importlib.util

                dashboard_router_path = dashboard_path / "router.py"
                if dashboard_router_path.exists():
                    spec = importlib.util.spec_from_file_location(
                        "dashboard_router", dashboard_router_path
                    )
                    dashboard_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(dashboard_module)
                    dashboard_router = dashboard_module.dashboard_router

                    # Include dashboard router
                    self.app.include_router(
                        dashboard_router, prefix="/dashboard", tags=["Dashboard"]
                    )
                    logger.info("✅ Unified Dashboard integrated successfully")
                else:
                    logger.warning("⚠️ Dashboard router not found")
            else:
                logger.info("ℹ️ Dashboard directory not found, will use default routes")
        except Exception as e:
            logger.warning(f"⚠️ Dashboard setup failed: {e}")
            logger.exception("Dashboard setup error details:")

    async def _add_core_routes(self) -> None:
        """Add core platform routes."""

        @self.app.get("/")
        async def root():
            """Platform root - redirect to dashboard or main app."""
            return RedirectResponse(url="/dashboard", status_code=302)

        @self.app.get("/health")
        async def health_check():
            """Platform health check."""
            return {
                "status": "healthy",
                "platform": "Yaz Healthcare Platform",
                "version": "4.0.0",
                "networking_enabled": self.networking_enabled,
                "loaded_apps": list(self.apps_loaded.keys()),
                "capabilities": {
                    "local_collaboration": self.networking_enabled,
                    "p2p_networking": hasattr(self, "p2p_network"),
                    "real_time_sync": self.collaboration_engine is not None,
                    "multi_domain": len(self.apps_loaded) > 1,
                },
            }

        @self.app.get("/platform/status")
        async def platform_status():
            """Detailed platform status."""
            status = {
                "platform": "Yaz Healthcare Platform",
                "version": "4.0.0",
                "uptime": "active",
                "applications": {},
            }

            for app_name, config in self.apps_loaded.items():
                status["applications"][app_name] = {
                    "name": config["name"],
                    "description": config["description"],
                    "status": "operational",
                    "endpoints": [config["prefix"] or "/"],
                }

            if self.networking_enabled:
                status["networking"] = {
                    "local_network": "operational",
                    "collaboration": "active",
                    "monitoring": "enabled",
                }

                if hasattr(self, "p2p_network"):
                    status["networking"]["p2p"] = "operational"

            return status

        @self.app.get("/platform/collaboration")
        async def collaboration_status():
            """Get collaboration status."""
            if not self.networking_enabled:
                return {"collaboration": "disabled", "reason": "networking not enabled"}

            try:
                peers = (
                    len(self.local_network.peers)
                    if hasattr(self, "local_network")
                    else 0
                )
                return {
                    "collaboration": "active",
                    "connected_peers": peers,
                    "real_time_sync": True,
                    "features": [
                        "live_editing",
                        "presence_awareness",
                        "conflict_resolution",
                    ],
                }
            except Exception as e:
                return {"collaboration": "error", "message": str(e)}


# Global platform instance
unified_platform = UnifiedYazPlatform()


async def create_app(**kwargs) -> FastAPI:
    """Create the unified Yaz platform application."""
    return await unified_platform.create_app(**kwargs)


def main() -> None:
    """Main entry point for unified platform."""
    parser = argparse.ArgumentParser(description="Yaz Healthcare Platform - Unified")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument(
        "--apps", default="all", help="Apps to load (comma-separated or 'all')"
    )
    parser.add_argument(
        "--networking", action="store_true", default=True, help="Enable networking"
    )
    parser.add_argument(
        "--p2p", action="store_true", default=True, help="Enable P2P networking"
    )
    parser.add_argument(
        "--ble-mesh", action="store_true", default=False, help="Enable BLE mesh"
    )
    parser.add_argument(
        "--multi-vm", action="store_true", default=False, help="Enable multi-VM"
    )

    args = parser.parse_args()

    # Determine apps to load
    if args.apps == "all":
        apps_to_load = ["surge", "clinica", "educa", "insura", "move"]
    else:
        apps_to_load = [app.strip() for app in args.apps.split(",")]

    # Create application
    app = asyncio.run(
        create_app(
            enable_networking=args.networking,
            enable_p2p=args.p2p,
            enable_ble_mesh=args.ble_mesh,
            enable_multi_vm=args.multi_vm,
            apps_to_load=apps_to_load,
        )
    )

    logger.info("🚀 Yaz Healthcare Platform - Unified Edition")
    logger.info(f"🌐 Platform running on http://{args.host}:{args.port}")
    logger.info("🎯 Access Points:")
    logger.info("   🏥 Dashboard: http://localhost:8000/dashboard")
    logger.info("   🔬 Surgery (Surge): http://localhost:8000/")
    logger.info("   🏥 Clinical (Clinica): http://localhost:8000/clinica")
    logger.info("   📚 Education (Educa): http://localhost:8000/educa")
    logger.info("   🛡️ Insurance (Insura): http://localhost:8000/insura")
    logger.info("   🚚 Logistics (Move): http://localhost:8000/move")
    logger.info("   📊 API Documentation: http://localhost:8000/api/docs")
    logger.info("   ❤️ Health Check: http://localhost:8000/health")

    if args.networking:
        logger.info("🌐 Advanced Networking: ENABLED")
        logger.info("   👥 Local Collaboration: Active")
        if args.p2p:
            logger.info("   🔗 P2P Networking: Active")
        logger.info("   🤝 Real-time Collaboration: Ready")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=False,  # Disable reload for production stability
        log_level="info",
    )


if __name__ == "__main__":
    main()
