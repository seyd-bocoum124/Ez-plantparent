from pydantic import BaseModel, Field

from entities.models import MaintenanceSheet
from entities.repositories import Repository
from entities.exceptions import NotFoundException, IllegalArgumentException, DatabaseConflictError

import logging
logger = logging.getLogger(__name__)

class GetMaintenanceSheetParams(BaseModel):
    sheet_id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)


class GetMaintenanceSheetByIdAction:
    def __init__(self, repository: Repository):
        self._repository = repository

    def execute(self, params: GetMaintenanceSheetParams) -> MaintenanceSheet:
        maintenance_sheet = self._try_get_maintenance_sheet_by_id(params.sheet_id)

        _check_maintenance_sheet_belong_to_user(maintenance_sheet, params.user_id)

        return maintenance_sheet


    # Service methods
    def _try_get_maintenance_sheet_by_id(self, sheet_id:int) -> MaintenanceSheet:
        maintenance_sheet = self._repository.get_maintenance_sheet_by_id(sheet_id)
        if not maintenance_sheet:
            raise NotFoundException(f"Maintenance sheet with id: {sheet_id} not found.")
        return maintenance_sheet

def _check_maintenance_sheet_belong_to_user(maintenance_sheet: MaintenanceSheet, user_id:int):
    if maintenance_sheet.user_id != user_id:
        raise IllegalArgumentException("The maintenance sheet dont belong to the user")
