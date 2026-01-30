from fastapi import APIRouter, Depends
from entities.repositories import Repository
from infrastructure.database import Database, get_db
from typing import List
from entities.exceptions import NotFoundException, IllegalArgumentException

from usecases.ManageMaintenanceSchedules.GetMaintenanceSchedule.GetMaintenanceSheetAction import \
    GetMaintenanceSchedulesAction
from usecases.ManageMaintenanceSchedules.GetMaintenanceSchedule.MaintenanceScheduleOutModel import MaintenanceScheduleOut
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer

router = APIRouter()

import logging
logger = logging.getLogger(__name__)


@router.get("/maintenance-schedule", response_model=List[MaintenanceScheduleOut])
def get_maintenance_sheet(
        db: Database = Depends(get_db),
        current = Depends(get_current_user_from_bearer)
    ):
    repository = Repository(db)
    try:
        schedule = GetMaintenanceSchedulesAction(repository).execute(current.user_id)
        return [MaintenanceScheduleOut.model_validate(item) for item in schedule]

    except (NotFoundException, IllegalArgumentException) as e:
        logger.info("%s: %s", type(e).__name__, e)




