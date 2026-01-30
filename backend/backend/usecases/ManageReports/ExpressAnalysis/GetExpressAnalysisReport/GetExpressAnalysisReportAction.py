from entities.exceptions import NotFoundException, UnauthorizedError
from entities.models import ExpressAnalysisReport
from infrastructure.database import get_db
from entities.repositories import Repository
import logging

from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class GetExpressAnalysisReportAction:
    def __init__(self, repo:Repository):
        if repo is None:
            db = get_db()
            self.repo = Repository(db)

        else:
            self.repo = repo


    # TODO (PLM) use a pydantic model for params
    def execute(self, report_id, user_id) -> ExpressAnalysisReport:
        report_analysis = self.repo.get_express_analysis_report_by_id(
            report_id)

        if report_analysis is None:
            raise NotFoundException(f"The report with id {report_id} not found")

        plant = self.repo.get_maintenance_sheet_by_id(report_analysis.plant_id)
        
        # TODO (PLM) make not needing a cast
        if plant is None or plant.user_id != int(user_id):
            raise UnauthorizedError(f"The user {user_id} cannot access to report {report_id}")

        return report_analysis