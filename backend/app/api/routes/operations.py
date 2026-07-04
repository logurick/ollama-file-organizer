from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import FileOperation

router = APIRouter(prefix="/operations", tags=["operations"])


@router.get("")
def list_operations(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[dict]:
    items = db.scalars(
        select(FileOperation).order_by(FileOperation.id.desc()).limit(limit)
    ).all()
    return [
        {
            "id": item.id,
            "file_record_id": item.file_record_id,
            "operation_type": item.operation_type,
            "status": item.status,
            "dry_run": item.dry_run,
            "executed_at": item.executed_at,
            "undone_at": item.undone_at,
        }
        for item in items
    ]
