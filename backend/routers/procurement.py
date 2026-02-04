"""
Intelligence Hub Procurement API Router

Provides endpoints for pharmaceutical bid evaluation using multi-agent system.
"""
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from backend.models.procurement import (
    BidAnalysisRequest,
    BidAnalysisResponse,
    TechnicalAnalysis,
    RiskAssessment,
    FinancialAnalysis,
    FinalRecommendation
)
from backend.services.procurement_agents import get_orchestrator
from backend.config import settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/procurement", tags=["procurement"])


@router.post("/analyze-bid", response_model=BidAnalysisResponse)
async def analyze_bid(
    file: UploadFile = File(..., description="Bid PDF document"),
    supplier_name: str = Form(..., description="Name of the supplier"),
    bid_price: float = Form(..., gt=0, description="Total bid price"),
    quantity: int = Form(..., gt=0, description="Quantity of units"),
    material_type: str = Form(default="api_base", description="Material type (api_base, excipient, packaging)")
):
    """
    Analyze a pharmaceutical bid using the Intelligence Hub multi-agent system.
    
    This endpoint orchestrates the following agents:
    - **TechnicalAgent**: Analyzes technical specifications from bid PDF
    - **RiskAgent**: Evaluates supplier risk (financial, ESG, red flags)
    - **FinancialAgent**: Performs should-cost modeling and pricing analysis
    - **Orchestrator**: Aggregates results and generates executive summary
    
    All decisions are logged for GxP compliance and audit trail.
    
    Args:
        file: Bid PDF document to analyze
        supplier_name: Name of the supplier submitting the bid
        bid_price: Total bid price in USD
        quantity: Quantity of units being bid
        material_type: Type of material (api_base, excipient, packaging)
        
    Returns:
        BidAnalysisResponse with complete evaluation and recommendation
        
    Raises:
        HTTPException: 400 if invalid file, 500 if analysis fails
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a PDF"
            )
        
        # Create temporary directory for bid PDFs
        temp_dir = Path(settings.pdf_storage_path) / "bids" / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file temporarily
        file_path = temp_dir / file.filename
        
        # Write file to disk
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Analyzing bid from {supplier_name}: {file.filename}")
        
        # Get orchestrator and run evaluation
        orchestrator = await get_orchestrator()
        result = await orchestrator.evaluate_bid(
            pdf_path=str(file_path),
            supplier_name=supplier_name,
            bid_price=bid_price,
            quantity=quantity
        )
        
        # Clean up temporary file
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete temp file {file_path}: {e}")
        
        # Convert to response model
        response = BidAnalysisResponse(
            success=True,
            supplier=result["supplier"],
            overall_score=result["overall_score"],
            weighted_scores=result["weighted_scores"],
            technical_analysis=TechnicalAnalysis(**result["technical_analysis"]),
            risk_assessment=RiskAssessment(**result["risk_assessment"]),
            financial_analysis=FinancialAnalysis(**result["financial_analysis"]),
            executive_summary=result["executive_summary"],
            final_recommendation=FinalRecommendation(**result["final_recommendation"]),
            processing_time_seconds=result["processing_time_seconds"],
            timestamp=result["timestamp"]
        )
        
        logger.info(
            f"Bid analysis complete for {supplier_name}: "
            f"Score={result['overall_score']:.1f}, "
            f"Decision={result['final_recommendation']['decision']}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing bid: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze bid: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Intelligence Hub service.
    
    Returns:
        Service status and configuration
    """
    return {
        "status": "operational",
        "service": "Intelligence Hub",
        "agents": ["TechnicalAgent", "RiskAgent", "FinancialAgent", "Orchestrator"],
        "compliance": "GxP & 21 CFR Part 11"
    }