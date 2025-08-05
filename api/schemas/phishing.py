from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class EmailAnalysisRequest(BaseModel):
    sender: str = Field(..., max_length=255)
    subject: str = Field(..., max_length=255)
    body: str


class EmailAnalysisResponse(BaseModel):
    id: int
    status: str


class PhishingAnalysisResult(BaseModel):
    id: int
    status: str
    sender: str
    subject: str
    body: str
    risk_score: Optional[int] = None
    justification: Optional[str] = None
    indicators_of_compromise: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
