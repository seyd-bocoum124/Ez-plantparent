from entities.exceptions import DatabaseConflictError
from infrastructure.database import get_db
from entities.repositories import Repository
import logging

from usecases.ManageReports.Watering.GetWateringReport.GetWateringReportAction import GetWateringReportAction

logger = logging.getLogger(__name__)

class DeleteWateringReportAction:
    def __init__(self, repo:Repository):
        if repo is None:
            db = get_db()
            self.repo = Repository(db)

        else:
            self.repo = repo

    def _check_watering_report_exist(self, report_id, user_id):
        GetWateringReportAction(self.repo).execute(report_id, user_id)

    def execute(self, report_id, user_id):
        self._check_watering_report_exist(report_id, user_id)

        deleted =  self.repo.delete_watering_report_by_id(report_id)
        if not deleted:
            raise DatabaseConflictError("A delete conflict happened")

        return deleted

