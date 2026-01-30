from fastapi import APIRouter, Depends
from entities.repositories import Repository
from infrastructure.database import Database, get_db
from usecases.ManageFicheEntretien.CreateMaintenanceSheet.CreateByName.MaintenanceSheetOutModel import MaintenanceSheetOut
from entities.exceptions import NotFoundException, IllegalArgumentException
from usecases.ManageFicheEntretien.GetMaintenanceSheet.GetMaintenanceSheetAction import GetMaintenanceSheetByIdAction, \
    GetMaintenanceSheetParams
from fastapi import HTTPException

from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer

router = APIRouter()

import logging
logger = logging.getLogger(__name__)


@router.get("/maintenance-sheets/{fiche_id}", response_model= MaintenanceSheetOut)
def get_maintenance_sheet(
        fiche_id: int,
        db: Database = Depends(get_db),
        current = Depends(get_current_user_from_bearer)
    ):
    repository = Repository(db)
    try:
        params = GetMaintenanceSheetParams(sheet_id=fiche_id, user_id=current.user_id)
        sheet = GetMaintenanceSheetByIdAction(repository).execute(params)
        return MaintenanceSheetOut.model_validate(sheet)

    except (NotFoundException, IllegalArgumentException) as e:
        logger.info("%s: %s", type(e).__name__, e)
        raise HTTPException(
            status_code=404,
            detail=f"the maintenance sheet with id {fiche_id} cant be found"
        )




