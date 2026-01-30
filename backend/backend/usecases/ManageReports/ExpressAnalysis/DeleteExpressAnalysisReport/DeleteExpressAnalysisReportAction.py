from entities.exceptions import DatabaseConflictError
from infrastructure.database import get_db
from entities.repositories import Repository
from usecases.ManageReports.ExpressAnalysis.GetExpressAnalysisReport.GetExpressAnalysisReportAction import \
    GetExpressAnalysisReportAction
import logging
logger = logging.getLogger(__name__)

class DeleteExpressAnalysisReportAction:
    def __init__(self, repo:Repository):
        if repo is None:
            db = get_db()
            self.repo = Repository(db)

        else:
            self.repo = repo

    def _check_analysis_report_exist(self, report_id, user_id):
        GetExpressAnalysisReportAction(self.repo).execute(report_id, user_id)

    def execute(self, report_id, user_id):
        self._check_analysis_report_exist(report_id, user_id)

        deleted =  self.repo.delete_express_analysis_report_by_id(report_id)
        if not deleted:
            raise DatabaseConflictError("A delete conflict happened")

        return deleted

