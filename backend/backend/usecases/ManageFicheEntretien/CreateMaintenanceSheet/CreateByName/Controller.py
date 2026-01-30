from fastapi import APIRouter, HTTPException, Depends

from entities.repositories import Repository
from infrastructure.database import Database, get_db

import logging

from usecases.ManageFicheEntretien.CreateMaintenanceSheet.CreateByName.CreateMaintenanceSheetAction import \
    CreateMaintenanceSheetParams, CreateMaintenanceSheetAction
from usecases.ManageFicheEntretien.CreateMaintenanceSheet.CreateByName.MaintenanceSheetOutModel import MaintenanceSheetOut
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/maintenance-sheets",
    response_model=MaintenanceSheetOut,
    status_code=201
)
def create_maintenance_sheet(params: CreateMaintenanceSheetParams, db: Database = Depends(get_db), current = Depends(get_current_user_from_bearer)):
    repo = Repository(db)
    maintenance_sheet = CreateMaintenanceSheetAction(repo).execute(params, current.user_id)
    try:
        return MaintenanceSheetOut.model_validate(maintenance_sheet)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Erreur interne: %s", e)
        raise HTTPException(status_code=500, detail="Erreur interne")

