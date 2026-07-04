from fastapi import APIRouter, HTTPException
from app.core.config import get_settings
from app.services.ollama_client import OllamaClient, OllamaError

router = APIRouter(prefix="/ollama", tags=["ollama"])

@router.get("/status")
async def status() -> dict:
    try:
        data = await OllamaClient(get_settings()).status()
        return {"ok": True, "models": data.get("models", [])}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Ollamaへ接続できません") from exc

@router.post("/test")
async def test() -> dict:
    settings = get_settings()
    try:
        decision = await OllamaClient(settings).classify(filename="テスト見積書.pdf", extension=".pdf", size=1234, extracted_text="御見積書 株式会社ABC 御中 合計金額 100,000円")
        return {"ok": True, "result": decision.model_dump(mode="json")}
    except OllamaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
