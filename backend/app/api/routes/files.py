from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import FileRecord

router = APIRouter(prefix="/files", tags=["files"])

@router.get("")
def list_files(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    items = db.scalars(select(FileRecord).order_by(FileRecord.id.desc()).limit(limit)).all()
    return [{"id": item.id, "filename": item.filename, "relative_path": item.relative_path, "extension": item.extension, "size": item.size, "status": item.status} for item in items]
