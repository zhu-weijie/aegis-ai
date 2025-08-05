from pydantic import BaseModel, Field


class EmailAnalysisRequest(BaseModel):
    sender: str = Field(..., max_length=255)
    subject: str = Field(..., max_length=255)
    body: str


class EmailAnalysisResponse(BaseModel):
    id: int
    status: str
