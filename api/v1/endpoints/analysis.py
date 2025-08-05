from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.phishing import PhishingAnalysis
from api.schemas.phishing import EmailAnalysisRequest, EmailAnalysisResponse

router = APIRouter()


@router.post("/analyze/email", response_model=EmailAnalysisResponse)
def analyze_email(request: EmailAnalysisRequest, db: Session = Depends(get_db)):
    db_analysis = PhishingAnalysis(
        sender=request.sender,
        subject=request.subject,
        body=request.body,
    )

    db.add(db_analysis)
    db.commit()

    db.refresh(db_analysis)

    return db_analysis
