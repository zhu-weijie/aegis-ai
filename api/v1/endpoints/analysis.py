from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.models.phishing import PhishingAnalysis
from api.schemas.phishing import (
    EmailAnalysisRequest,
    EmailAnalysisResponse,
    PhishingAnalysisResult,
)
from api.services.phishing_analyzer import analyze_email_content

router = APIRouter()


def run_phishing_analysis(
    analysis_id: int, sender: str, subject: str, body: str, db: Session
):
    print(f"Starting analysis for task ID: {analysis_id}")
    analysis_result = analyze_email_content(sender, subject, body)

    db_analysis = (
        db.query(PhishingAnalysis).filter(PhishingAnalysis.id == analysis_id).first()
    )
    if db_analysis:
        db_analysis.justification = analysis_result.get("justification")
        db_analysis.risk_score = analysis_result.get("risk_score")
        db_analysis.indicators_of_compromise = analysis_result.get("iocs")
        db_analysis.status = "COMPLETED"
        db.commit()
        print(f"Analysis complete for task ID: {analysis_id}")
    else:
        print(f"Could not find analysis task ID: {analysis_id} to update.")


@router.post("/analyze/email", response_model=EmailAnalysisResponse)
def analyze_email(
    request: EmailAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    db_analysis = PhishingAnalysis(
        sender=request.sender,
        subject=request.subject,
        body=request.body,
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    background_tasks.add_task(
        run_phishing_analysis,
        db_analysis.id,
        db_analysis.sender,
        db_analysis.subject,
        db_analysis.body,
        db,
    )

    return db_analysis


@router.get("/analyze/email/{analysis_id}", response_model=PhishingAnalysisResult)
def get_analysis_result(analysis_id: int, db: Session = Depends(get_db)):
    db_analysis = (
        db.query(PhishingAnalysis).filter(PhishingAnalysis.id == analysis_id).first()
    )
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return db_analysis
