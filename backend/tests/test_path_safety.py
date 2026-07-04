from pathlib import Path

import pytest

from app.services.path_safety import PathSafetyError, ensure_within_root, safe_destination, sanitize_component


def test_rejects_path_outside_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    with pytest.raises(PathSafetyError):
        ensure_within_root(tmp_path / "outside.txt", root)


def test_safe_destination_rejects_absolute(tmp_path: Path) -> None:
    with pytest.raises(PathSafetyError):
        safe_destination(tmp_path, Path("/etc/passwd"))


def test_sanitize_windows_forbidden_chars() -> None:
    assert sanitize_component('a<b>:c"d/e\\f|g?h*') == "a_b__c_d_e_f_g_h_"


def test_reserved_windows_name_is_prefixed() -> None:
    assert sanitize_component("CON") == "_CON"
