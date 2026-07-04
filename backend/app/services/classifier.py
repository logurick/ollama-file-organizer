from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import Settings
from app.models.entities import AnalysisResult, Approval, FileRecord
from app.schemas.analysis import ClassificationDecision
from app.services.extractor import ExtractionError, extract_text
from app.services.ollama_client import OllamaClient
from app.services.rules_engine import classify_by_rule


def status_from_confidence(confidence: float, settings: Settings) -> str:
    if confidence >= settings.auto_confidence_threshold:
        return "auto_candidate"
    if confidence >= settings.review_confidence_threshold:
        return "pending_approval"
    return "on_hold"


async def analyze_file(db: Session, record: FileRecord, settings: Settings) -> AnalysisResult:
    path = Path(record.absolute_path)
    rule_decision = classify_by_rule(record.filename)
    try:
        text = extract_text(path, settings.max_extracted_text_length)
    except ExtractionError:
        text = ""
    decision: ClassificationDecision = rule_decision or await OllamaClient(settings).classify(filename=record.filename, extension=record.extension, size=record.size, extracted_text=text)
    result = AnalysisResult(
        file_record_id=record.id, category_id=decision.category_id, subcategory_id=decision.subcategory_id,
        customer_name=decision.customer_name, document_date=decision.document_date,
        suggested_filename=decision.suggested_filename, summary=decision.summary, tags=decision.tags,
        confidence=decision.confidence, reason=decision.reason,
        model_name="rule-engine" if rule_decision else settings.ollama_model,
        prompt_version="v1", raw_response=decision.model_dump(mode="json"),
    )
    db.add(result)
    db.flush()
    record.status = status_from_confidence(decision.confidence, settings)
    if record.status == "pending_approval":
        db.add(Approval(file_record_id=record.id, analysis_result_id=result.id, status="pending"))
    db.commit()
    db.refresh(result)
    return result
