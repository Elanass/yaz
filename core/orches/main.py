# orches/main.py
"""
Main entrypoint for the orchestrator module.
"""

from core.managers.orchestration import config, logger, container
from core.licensing_manager import licensing_manager

# Import each module’s public entrypoint
from visioner.entrypoint import serve_visioner
from parent.entrypoint import ParentService
from generalservices.entrypoint import GeneralServicesApp
from specificapps.entrypoint import SpecificAppsApp
from operators.clinic import ClinicOperator
from operators.imobi import ImobiOperator
from operators.mobi import MobiOperator
from operators.arxiv import ArxivOperator
from operators.insure import InsureOperator

def run():
    """Run the orchestrator."""
    logger.info("Starting orchestration via ‘orches’")
    
    # Load licenses
    licensing_manager.load_licenses()

    # Example: initialize core services
    general_app = GeneralServicesApp(licensing_manager)
    specific_app = SpecificAppsApp(licensing_manager)
    
    # Wire in operators
    clinic = ClinicOperator(licensing_manager)
    imobi  = ImobiOperator(licensing_manager)
    mobi   = MobiOperator(licensing_manager)
    arxiv  = ArxivOperator(licensing_manager)
    insure = InsureOperator(licensing_manager)
    
    # Boot modules (adjust order/args as needed)
    serve_visioner(app=general_app)
    ParentService(container).start()
    general_app.start()
    specific_app.start()
    clinic.start()
    imobi.start()
    mobi.start()
    arxiv.start()
    insure.start()

if __name__ == "__main__":
    run()