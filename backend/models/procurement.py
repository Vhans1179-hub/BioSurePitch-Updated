"""
Pydantic models for Intelligence Hub procurement endpoints.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class BidAnalysisRequest(BaseModel):
    """Request model for bid analysis."""
    supplier_name: str = Field(..., description="Name of the supplier")
    bid_price: float = Field(..., gt=0, description="Total bid price")
    quantity: int = Field(..., gt=0, description="Quantity of units")
    material_type: str = Field(default="api_base", description="Type of material (api_base, excipient, packaging)")


class TechnicalAnalysis(BaseModel):
    """Technical analysis results."""
    supplier: str
    extracted_specs: Dict[str, Any]
    sop_parameters: Dict[str, Any]
    deviations: List[Dict[str, Any]]
    compliance_score: float
    status: str
    raw_extraction: Optional[str] = None
    error: Optional[str] = None


class RiskAssessment(BaseModel):
    """Risk assessment results."""
    supplier: str
    financial_score: float
    esg_score: float
    overall_risk_score: float
    red_flags: List[str]
    status: str
    recommendation: str


class FinancialAnalysis(BaseModel):
    """Financial analysis results."""
    supplier: str
    bid_price: float
    quantity: int
    should_cost_breakdown: Dict[str, Any]
    variance: float
    variance_threshold: str
    status: str
    recommendation: str


class FinalRecommendation(BaseModel):
    """Final recommendation from orchestrator."""
    decision: str
    confidence: str
    reason: str
    requires_human_approval: bool
    next_steps: List[str]


class BidAnalysisResponse(BaseModel):
    """Response model for bid analysis."""
    success: bool
    supplier: str
    overall_score: float
    weighted_scores: Dict[str, float]
    technical_analysis: TechnicalAnalysis
    risk_assessment: RiskAssessment
    financial_analysis: FinancialAnalysis
    executive_summary: str
    final_recommendation: FinalRecommendation
    processing_time_seconds: float
    timestamp: str
    error: Optional[str] = None