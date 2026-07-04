from datetime import date
from pathlib import Path
from string import Formatter
from app.schemas.analysis import ClassificationDecision
from app.services.path_safety import PathSafetyError, safe_destination, sanitize_component

ALLOWED_TEMPLATE_FIELDS = {"year", "month", "day", "customer_name", "category", "subcategory"}


def _date_parts(value: str | None) -> tuple[str, str, str]:
    if value:
        try:
            parsed = date.fromisoformat(value[:10])
            return f"{parsed.year:04d}", f"{parsed.month:02d}", f"{parsed.day:02d}"
        except ValueError:
            pass
    today = date.today()
    return f"{today.year:04d}", f"{today.month:02d}", f"{today.day:02d}"


def resolve_destination(root: Path, template: str, decision: ClassificationDecision) -> Path:
    fields = {name for _, name, _, _ in Formatter().parse(template) if name}
    unknown = fields - ALLOWED_TEMPLATE_FIELDS
    if unknown:
        raise PathSafetyError(f"未許可のテンプレート変数です: {sorted(unknown)}")
    year, month, day = _date_parts(decision.document_date)
    values = {
        "year": year, "month": month, "day": day,
        "customer_name": sanitize_component(decision.customer_name or "不明顧客"),
        "category": sanitize_component(decision.category_id),
        "subcategory": sanitize_component(decision.subcategory_id or "その他"),
    }
    return safe_destination(root, Path(template.format(**values)))
