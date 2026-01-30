from fastapi import Depends, APIRouter
from entities.repositories import Repository
from infrastructure.database import Database, get_db
from typing import List

from usecases.ManageFicheEntretien.CreateMaintenanceSheet.CreateByName.MaintenanceSheetOutModel import MaintenanceSheetOut
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer

router = APIRouter()
@router.get("/maintenance-sheets", response_model=List[MaintenanceSheetOut])
def list_maintenance_sheets(db: Database = Depends(get_db), current = Depends(get_current_user_from_bearer)):
    repository = Repository(db)
    sheets = repository.list_all_maintenance_sheets_by_user_id(current.user_id)
    return [MaintenanceSheetOut.model_validate(s) for s in sheets]