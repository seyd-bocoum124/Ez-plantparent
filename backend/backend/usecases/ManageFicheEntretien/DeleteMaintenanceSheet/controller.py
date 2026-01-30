import logging

from fastapi import Depends, APIRouter, HTTPException, Response, status

from entities.exceptions import NotFoundException, IllegalArgumentException, DatabaseConflictError
from infrastructure.database import Database, get_db
from entities.repositories import Repository
from usecases.ManageFicheEntretien.DeleteMaintenanceSheet.DeleteMaintenanceSheetAction import \
    DeleteMaintenanceSheetAction, DeleteMaintenanceSheetParams
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer

router = APIRouter()


logger = logging.getLogger(__name__)

@router.delete("/maintenance-sheets/{sheet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance_sheet(
    sheet_id: int,
    db: Database = Depends(get_db),
    current = Depends(get_current_user_from_bearer),
):
    repository = Repository(db)
    try:
        params = DeleteMaintenanceSheetParams(sheet_id=sheet_id, user_id=current.user_id)

        DeleteMaintenanceSheetAction(repository).execute(params)

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except (NotFoundException, IllegalArgumentException) as e:
        logger.info("%s: %s", type(e).__name__, e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"the maintenance sheet with id {sheet_id} cant be found"
        )
    except DatabaseConflictError as e:
        logger.info("DatabaseConflictError:%s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The maintenance sheet {sheet_id} could not had been deleted. Conflit or database constraint."
        )
    except Exception as e:
        logger.info("Exception:%s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne")

