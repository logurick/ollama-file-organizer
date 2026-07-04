from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import WatchFolder
from app.schemas.watch_folder import WatchFolderCreate, WatchFolderRead, WatchFolderUpdate
from app.services.path_safety import PathSafetyError, ensure_within_root

router = APIRouter(prefix="/watch-folders", tags=["watch-folders"])


@router.get("", response_model=list[WatchFolderRead])
def list_watch_folders(db: Session = Depends(get_db)) -> list[WatchFolder]:
    return list(db.scalars(select(WatchFolder).order_by(WatchFolder.id)))


@router.post("", response_model=WatchFolderRead, status_code=201)
def create_watch_folder(payload: WatchFolderCreate, db: Session = Depends(get_db)) -> WatchFolder:
    try:
        ensure_within_root(Path(payload.inbox_path), Path(payload.root_path))
    except PathSafetyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    item = WatchFolder(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{folder_id}", response_model=WatchFolderRead)
def get_watch_folder(folder_id: int, db: Session = Depends(get_db)) -> WatchFolder:
    item = db.get(WatchFolder, folder_id)
    if item is None:
        raise HTTPException(status_code=404, detail="監視フォルダが見つかりません")
    return item


@router.put("/{folder_id}", response_model=WatchFolderRead)
def update_watch_folder(folder_id: int, payload: WatchFolderUpdate, db: Session = Depends(get_db)) -> WatchFolder:
    item = db.get(WatchFolder, folder_id)
    if item is None:
        raise HTTPException(status_code=404, detail="監視フォルダが見つかりません")

    try:
        ensure_within_root(Path(payload.inbox_path), Path(payload.root_path))
    except PathSafetyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item
