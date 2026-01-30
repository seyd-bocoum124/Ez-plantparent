from fastapi import HTTPException

from fastapi import APIRouter, Depends

from entities.exceptions import NotFoundException, DatabaseConflictError, UnauthorizedError
from entities.repositories import Repository
from infrastructure.database import Database, get_db
from usecases.ManageReports.Watering.DeleteWateringReport.DeleteWateringReportAction import DeleteWateringReportAction
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer

router = APIRouter()

import logging
logger = logging.getLogger(__name__)


@router.delete("/reports/watering/{report_id}", status_code=204)
def delete_watering_report(report_id: int, db: Database = Depends(get_db), current = Depends(get_current_user_from_bearer)):
    repository = Repository(db)
    try:
        return DeleteWateringReportAction(repository).execute(report_id, current.user_id)
    except (NotFoundException, UnauthorizedError) as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500,
                            detail="Une erreure interne s'est produite!")