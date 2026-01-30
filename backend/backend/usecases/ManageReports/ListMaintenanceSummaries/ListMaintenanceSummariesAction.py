from pydantic import BaseModel, Field

from entities.models import MaintenanceSummary
from entities.repositories import Repository
from entities.exceptions import IllegalArgumentException

import logging

from usecases.ManageFicheEntretien.GetMaintenanceSheet.GetMaintenanceSheetAction import GetMaintenanceSheetByIdAction, \
    GetMaintenanceSheetParams

logger = logging.getLogger(__name__)

class ListMaintenanceSummariesParams(BaseModel):
    sheet_id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)


class ListMaintenanceSummariesAction:
    def __init__(self, repository: Repository):
        self._repository = repository

    def execute(self, params: ListMaintenanceSummariesParams) -> list[MaintenanceSummary]:
        repository = self._repository

        self._check_maintenance_sheet_belong_to_user(params)

        return repository.list_maintenance_summaries(params.sheet_id, params.user_id)

    def _check_maintenance_sheet_belong_to_user(self, params: ListMaintenanceSummariesParams):
        res = GetMaintenanceSheetByIdAction(self._repository).execute(GetMaintenanceSheetParams(
            sheet_id=params.sheet_id,
            user_id=params.user_id,
        ))
        if not res:
            raise IllegalArgumentException("User dont own the plant")
