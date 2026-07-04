from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import FileRecord, WatchFolder

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
def dashboard(db: Session = Depends(get_db)):
    watch_count = db.scalar(select(func.count()).select_from(WatchFolder)) or 0
    status_rows = db.execute(select(FileRecord.status, func.count()).group_by(FileRecord.status)).all()
    return {"watch_folders": watch_count, "statuses": {status: count for status, count in status_rows}}
