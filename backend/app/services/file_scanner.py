import fnmatch
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import FileRecord, WatchFolder
from app.services.hashing import sha256_file
from app.services.path_safety import ensure_within_root, reject_symlink_escape


def _excluded(name: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def scan_watch_folder(db: Session, watch: WatchFolder) -> dict[str, int]:
    root = Path(watch.root_path)
    inbox = Path(watch.inbox_path)
    ensure_within_root(inbox, root)
    if not inbox.exists() or not inbox.is_dir():
        raise FileNotFoundError(f"監視フォルダが存在しません: {inbox}")
    allowed = {ext.lower() for ext in watch.allowed_extensions if ext}
    max_bytes = watch.max_file_size_mb * 1024 * 1024
    stats = {"discovered": 0, "updated": 0, "skipped": 0}
    for path in inbox.rglob("*"):
        if not path.is_file():
            continue
        if _excluded(path.name, watch.exclude_patterns) or (allowed and path.suffix.lower() not in allowed):
            stats["skipped"] += 1
            continue
        stat = path.stat()
        if stat.st_size > max_bytes:
            stats["skipped"] += 1
            continue
        ensure_within_root(path, root)
        reject_symlink_escape(path, root)
        absolute = str(path.resolve(strict=False))
        record = db.scalar(select(FileRecord).where(FileRecord.watch_folder_id == watch.id, FileRecord.absolute_path == absolute))
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
        relative = str(path.resolve(strict=False).relative_to(root.resolve(strict=False)))
        digest = sha256_file(path)
        mime_type, _ = mimetypes.guess_type(path.name)
        if record is None:
            db.add(FileRecord(watch_folder_id=watch.id, absolute_path=absolute, relative_path=relative, filename=path.name, extension=path.suffix.lower(), mime_type=mime_type, size=stat.st_size, sha256=digest, created_time=created, modified_time=modified, status="discovered"))
            stats["discovered"] += 1
        else:
            changed = record.size != stat.st_size or record.sha256 != digest
            record.relative_path = relative
            record.filename = path.name
            record.extension = path.suffix.lower()
            record.mime_type = mime_type
            record.size = stat.st_size
            record.sha256 = digest
            record.created_time = created
            record.modified_time = modified
            if changed:
                record.status = "discovered"
                stats["updated"] += 1
    db.commit()
    return stats
