from entities.exceptions import NotFoundException, UnauthorizedError
from entities.models import WateringReport
from infrastructure.database import get_db
from entities.repositories import Repository



class GetWateringReportAction:
    def __init__(self, repo:Repository):
        if repo is None:
            db = get_db()
            self.repo = Repository(db)

        else:
            self.repo = repo


    def execute(self, report_id, user_id) -> WateringReport:
        watering_report = self.repo.get_watering_report_by_id(report_id)

        if watering_report is None:
            raise NotFoundException(f"The report with id {report_id} not found")

        plant = self.repo.get_maintenance_sheet_by_id(watering_report.plant_id)

        # TODO (PLM) make not needing a cast
        if plant is None or plant.user_id != int(user_id):
            raise UnauthorizedError(f"The user {user_id} cannot access to report {report_id}")

        return watering_report