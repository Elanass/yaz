# orchestrator/main.py
"""
Main entrypoint for the orchestrator module.
"""

from core.config.platform_config import config
from core.services.logger import get_logger
from core.licensing_manager import licensing_manager

# Import APIs and services
from api.v1.main import api_router
from apps.generalservices.entrypoint import GeneralServicesApp
from apps.specificapps.entrypoint import SpecificAppsApp
from apps.visioner.entrypoint import serve_visioner
from core.operators.clinic import ClinicOperator
from core.operators.imobi import ImobiOperator
from core.operators.mobi import MobiOperator
from core.operators.arxiv import ArxivOperator
from core.operators.insure import InsureOperator

logger = get_logger("orchestrator")

def run():
    """Run the orchestrator."""
    logger.info("Starting orchestration")
    
    # Load licenses
    licensing_manager.load_licenses()

    # Initialize core services
    general_app = GeneralServicesApp(licensing_manager)
    specific_app = SpecificAppsApp(licensing_manager)
    
    # Additional initialization would go here
    logger.info("API router loaded: %s", api_router)

if __name__ == "__main__":
    run()