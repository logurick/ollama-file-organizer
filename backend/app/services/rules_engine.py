from app.schemas.analysis import ClassificationDecision

RULES = (
    (("見積書", "御見積"), "CUSTOMER_QUOTATION", "ファイル名に見積書を示す語が含まれるため"),
    (("請求書", "御請求"), "INVOICE", "ファイル名に請求書を示す語が含まれるため"),
    (("注文書", "発注書"), "PURCHASE_ORDER", "ファイル名に注文書を示す語が含まれるため"),
    (("議事録", "会議録"), "MEETING_MINUTES", "ファイル名に議事録を示す語が含まれるため"),
    (("仕様書",), "SPECIFICATION", "ファイル名に仕様書を示す語が含まれるため"),
    (("マニュアル", "手順書"), "MANUAL", "ファイル名にマニュアル・手順書を示す語が含まれるため"),
)


def classify_by_rule(filename: str) -> ClassificationDecision | None:
    normalized = filename.casefold()
    for keywords, category_id, reason in RULES:
        if any(keyword.casefold() in normalized for keyword in keywords):
            return ClassificationDecision(category_id=category_id, confidence=0.99, summary=f"ルールにより{category_id}へ分類", reason=reason, tags=[category_id])
    return None
