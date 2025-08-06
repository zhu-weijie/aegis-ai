from sqlalchemy import JSON, Column, Integer, String, Text

from .base import Base


class PhishingAnalysis(Base):
    __tablename__ = "phishing_analysis"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False, default="PENDING")
    sender = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    risk_score = Column(Integer, nullable=True)
    justification = Column(Text, nullable=True)
    indicators_of_compromise = Column(JSON, nullable=True)
    threat_intel_context = Column(JSON, nullable=True)
