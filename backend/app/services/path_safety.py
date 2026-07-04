from __future__ import annotations

import os
import re
from pathlib import Path

WINDOWS_FORBIDDEN_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
WINDOWS_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


class PathSafetyError(ValueError):
    pass


def _resolved(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError as exc:
        raise PathSafetyError(f"パスを解決できません: {path}") from exc


def ensure_within_root(path: Path, root: Path) -> Path:
    resolved_path = _resolved(path)
    resolved_root = _resolved(root)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise PathSafetyError(f"許可ルート外のパスです: {path}") from exc
    return resolved_path


def reject_symlink_escape(path: Path, root: Path) -> None:
    resolved_root = _resolved(root)
    current = path
    while True:
        if current.exists() and current.is_symlink():
            target = _resolved(current)
            try:
                target.relative_to(resolved_root)
            except ValueError as exc:
                raise PathSafetyError(f"シンボリックリンクが許可ルート外を指しています: {current}") from exc
        if current == current.parent or _resolved(current) == resolved_root:
            break
        current = current.parent


def sanitize_component(value: str, fallback: str = "不明") -> str:
    cleaned = WINDOWS_FORBIDDEN_CHARS.sub("_", value.strip()).rstrip(" .")
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        cleaned = fallback
    if cleaned.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned[:120]


def safe_destination(root: Path, relative: Path) -> Path:
    if relative.is_absolute():
        raise PathSafetyError("移動先には相対パスのみ指定できます")
    if any(part in {"..", ""} for part in relative.parts):
        raise PathSafetyError("不正な相対パスです")
    candidate = root.joinpath(*[sanitize_component(part) for part in relative.parts])
    return ensure_within_root(candidate, root)


def unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(1, 10000):
        candidate = path.with_name(f"{path.stem}_{index:03d}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise PathSafetyError("同名ファイルの採番上限に達しました")


def same_filesystem_path(a: Path, b: Path) -> bool:
    return os.path.normcase(str(_resolved(a))) == os.path.normcase(str(_resolved(b)))
