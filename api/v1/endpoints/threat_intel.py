from fastapi import APIRouter

from api.schemas.threat_intel import (
    TextIngestionRequest,
    ThreatIntelQueryRequest,
    ThreatIntelQueryResponse,
)
from api.services.threat_intel import ingest_text, query_threat_intel

router = APIRouter()


@router.post("/threat-intel/ingest")
def ingest_threat_intel(request: TextIngestionRequest):
    result = ingest_text(text=request.text)
    return result


@router.post("/threat-intel/query", response_model=ThreatIntelQueryResponse)
def query_threat_intel_endpoint(request: ThreatIntelQueryRequest):
    result = query_threat_intel(query=request.query)
    return result
