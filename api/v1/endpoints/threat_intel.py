from fastapi import APIRouter

from api.schemas.threat_intel import TextIngestionRequest
from api.services.threat_intel import ingest_text

router = APIRouter()


@router.post("/threat-intel/ingest")
def ingest_threat_intel(request: TextIngestionRequest):
    result = ingest_text(text=request.text)
    return result
