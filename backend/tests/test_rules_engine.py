from app.services.rules_engine import classify_by_rule


def test_rule_engine_classifies_quotation() -> None:
    result = classify_by_rule("2026-07-03_株式会社ABC_見積書.pdf")
    assert result is not None
    assert result.category_id == "CUSTOMER_QUOTATION"
    assert result.confidence == 0.99


def test_rule_engine_returns_none_for_unknown() -> None:
    assert classify_by_rule("scan001.pdf") is None
