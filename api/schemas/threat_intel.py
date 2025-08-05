from pydantic import BaseModel


class TextIngestionRequest(BaseModel):
    text: str


class ThreatIntelQueryRequest(BaseModel):
    query: str


class ThreatIntelQueryResponse(BaseModel):
    answer: str
    source_found: bool
