import shutil
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.entities import FileOperation, FileRecord, WatchFolder
from app.services.hashing import sha256_file
from app.services.path_safety import ensure_within_root, reject_symlink_escape, unique_destination


class FileOperationError(RuntimeError):
    pass


def move_file(db: Session, *, record: FileRecord, watch: WatchFolder, destination_dir: Path, new_filename: str | None, dry_run: bool) -> FileOperation:
    source = Path(record.absolute_path)
    root = Path(watch.root_path)
    ensure_within_root(source, root)
    ensure_within_root(destination_dir, root)
    reject_symlink_escape(source, root)
    if not source.exists() or not source.is_file():
        raise FileOperationError("移動元ファイルが存在しません")
    current_sha = sha256_file(source)
    if record.sha256 and current_sha != record.sha256:
        raise FileOperationError("解析後にファイル内容が変更されています")
    destination = unique_destination(destination_dir / (new_filename or source.name))
    ensure_within_root(destination, root)
    operation = FileOperation(file_record_id=record.id, operation_type="move", source_path=str(source), destination_path=str(destination), status="dry_run" if dry_run else "pending", dry_run=dry_run, source_sha256=current_sha)
    db.add(operation)
    db.flush()
    if dry_run:
        db.commit(); db.refresh(operation); return operation
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        operation.status = "completed"
        record.absolute_path = str(destination.resolve(strict=False))
        record.relative_path = str(destination.resolve(strict=False).relative_to(root.resolve(strict=False)))
        record.filename = destination.name
        record.status = "organized"
        db.commit(); db.refresh(operation); return operation
    except Exception as exc:
        operation.status = "failed"
        operation.error_message = str(exc)
        db.commit()
        raise FileOperationError("ファイル移動に失敗しました") from exc


def undo_operation(db: Session, operation: FileOperation, watch: WatchFolder) -> FileOperation:
    if operation.dry_run:
        raise FileOperationError("Dry Run操作はUndo対象ではありません")
    if operation.status != "completed" or operation.undone_at is not None:
        raise FileOperationError("Undoできない操作状態です")
    source = Path(operation.source_path)
    current = Path(operation.destination_path)
    root = Path(watch.root_path)
    ensure_within_root(source, root); ensure_within_root(current, root)
    if not current.exists(): raise FileOperationError("移動後ファイルが存在しません")
    if source.exists(): raise FileOperationError("元位置に同名ファイルが存在します")
    if operation.source_sha256 and sha256_file(current) != operation.source_sha256:
        raise FileOperationError("移動後ファイルのハッシュが一致しません")
    source.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(current), str(source))
    operation.undone_at = datetime.now(timezone.utc)
    operation.status = "undone"
    operation.file_record.absolute_path = str(source.resolve(strict=False))
    operation.file_record.filename = source.name
    operation.file_record.relative_path = str(source.resolve(strict=False).relative_to(root.resolve(strict=False)))
    operation.file_record.status = "discovered"
    db.commit(); db.refresh(operation); return operation
