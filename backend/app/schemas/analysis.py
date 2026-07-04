from pydantic import BaseModel, Field


class ClassificationDecision(BaseModel):
    category_id: str = Field(min_length=1, max_length=100)
    subcategory_id: str | None = Field(default=None, max_length=100)
    customer_name: str | None = Field(default=None, max_length=255)
    document_date: str | None = Field(default=None, max_length=32)
    suggested_filename: str | None = Field(default=None, max_length=255)
    tags: list[str] = Field(default_factory=list, max_length=20)
    summary: str = Field(default="", max_length=2000)
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(default="", max_length=2000)


class AnalysisRequest(BaseModel):
    force: bool = False
