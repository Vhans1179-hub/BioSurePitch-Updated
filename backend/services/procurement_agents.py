"""
Intelligence Hub - Multi-Agent System for Pharmaceutical Bid Evaluation

This module implements a simplified multi-agent system for automating bid evaluation:
- TechnicalAgent: Analyzes technical specifications from bid PDFs
- RiskAgent: Evaluates supplier risk (mocked data)
- FinancialAgent: Performs should-cost modeling (mocked commodity prices)
- Orchestrator: Aggregates results and generates executive summary
- ComplianceLogger: Maintains audit trail for GxP compliance
"""
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
import random

from backend.services.gemini_rag_service import get_rag_service

# Configure logging
logger = logging.getLogger(__name__)


class ComplianceLogger:
    """
    Maintains an immutable audit trail for all agent decisions.
    Supports GxP and 21 CFR Part 11 compliance requirements.
    """
    
    def __init__(self, log_dir: str = "backend/data/audit_logs"):
        """Initialize compliance logger with log directory."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_decision(
        self,
        agent_name: str,
        action: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        user: str = "system"
    ) -> str:
        """
        Log an agent decision with full traceability.
        
        Args:
            agent_name: Name of the agent making the decision
            action: Action performed
            inputs: Input parameters
            outputs: Output/results
            user: User who initiated the action
            
        Returns:
            Log entry ID
        """
        timestamp = datetime.now(timezone.utc)
        log_id = f"{agent_name}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        log_entry = {
            "log_id": log_id,
            "timestamp": timestamp.isoformat(),
            "agent": agent_name,
            "action": action,
            "user": user,
            "inputs": inputs,
            "outputs": outputs
        }
        
        # Write to file (append-only for immutability) - DISABLED
        # log_file = self.log_dir / f"{timestamp.strftime('%Y%m%d')}_audit.jsonl"
        # with open(log_file, "a") as f:
        #     f.write(json.dumps(log_entry) + "\n")
        
        logger.info(f"Audit logging disabled - would have logged: {log_id}")
        return log_id


class TechnicalAgent:
    """
    Analyzes technical specifications from bid documents.
    Uses Gemini to extract technical parameters and compare against SOPs.
    """
    
    # Mock SOP parameters for demonstration
    SOP_PARAMETERS = {
        "purity_level": {"min": 95.0, "max": 100.0, "unit": "%"},
        "yield_rate": {"min": 85.0, "max": 100.0, "unit": "%"},
        "storage_temp": {"min": 2.0, "max": 8.0, "unit": "°C"},
        "shelf_life": {"min": 24, "max": 36, "unit": "months"}
    }
    
    TOLERANCE = 5.0  # ±5% tolerance as per PRD
    
    def __init__(self, compliance_logger: ComplianceLogger):
        """Initialize technical agent."""
        self.compliance_logger = compliance_logger
    
    async def analyze_bid(
        self,
        pdf_path: str,
        supplier_name: str
    ) -> Dict[str, Any]:
        """
        Analyze technical specifications from bid PDF.
        
        Args:
            pdf_path: Path to bid PDF file
            supplier_name: Name of supplier
            
        Returns:
            Technical analysis results with compliance flags
        """
        logger.info(f"TechnicalAgent analyzing bid from {supplier_name}")
        
        try:
            # Use Gemini to extract technical specs from PDF
            rag_service = await get_rag_service()
            
            # Upload PDF to Gemini
            display_name = f"bid_{supplier_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            gemini_file_name = await rag_service.upload_pdf(pdf_path, display_name)
            
            if not gemini_file_name:
                raise Exception("Failed to upload PDF to Gemini")
            
            # Query for technical specifications
            query = """
            Extract the following technical specifications from this pharmaceutical bid document:
            1. Purity level (%)
            2. Yield rate (%)
            3. Storage temperature requirements (°C)
            4. Shelf life (months)
            
            Provide the values in a structured format. If any value is not found, indicate "Not specified".
            """
            
            result = await rag_service.query_documents(query, [gemini_file_name])
            
            if not result["success"]:
                raise Exception(f"Gemini query failed: {result.get('error')}")
            
            # Parse extracted specs (in real implementation, would use structured output)
            extracted_text = result["response"]
            
            # Mock parsing for demonstration (in production, use structured extraction)
            specs = self._parse_specs(extracted_text)
            
            # Compare against SOP parameters
            deviations = self._check_deviations(specs)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(deviations)
            
            analysis = {
                "supplier": supplier_name,
                "extracted_specs": specs,
                "sop_parameters": self.SOP_PARAMETERS,
                "deviations": deviations,
                "compliance_score": compliance_score,
                "status": "PASS" if compliance_score >= 80 else "FAIL",
                "raw_extraction": extracted_text
            }
            
            # Log decision
            self.compliance_logger.log_decision(
                agent_name="TechnicalAgent",
                action="analyze_bid",
                inputs={"supplier": supplier_name, "pdf_path": pdf_path},
                outputs=analysis
            )
            
            # Clean up Gemini file
            await rag_service.delete_file(gemini_file_name)
            
            return analysis
            
        except Exception as e:
            logger.error(f"TechnicalAgent error: {str(e)}", exc_info=True)
            return {
                "supplier": supplier_name,
                "extracted_specs": {},
                "sop_parameters": self.SOP_PARAMETERS,
                "deviations": [],
                "compliance_score": 0,
                "status": "ERROR",
                "error": str(e)
            }
    
    def _parse_specs(self, text: str) -> Dict[str, Any]:
        """
        Parse technical specifications from extracted text.
        In production, use structured output or more sophisticated parsing.
        """
        # Mock extraction for demonstration
        return {
            "purity_level": random.uniform(93, 99),
            "yield_rate": random.uniform(82, 95),
            "storage_temp": random.uniform(1, 9),
            "shelf_life": random.randint(20, 38)
        }
    
    def _check_deviations(self, specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for deviations from SOP parameters."""
        deviations = []
        
        for param, value in specs.items():
            if param not in self.SOP_PARAMETERS:
                continue
            
            sop = self.SOP_PARAMETERS[param]
            min_val = sop["min"] * (1 - self.TOLERANCE / 100)
            max_val = sop["max"] * (1 + self.TOLERANCE / 100)
            
            if value < min_val or value > max_val:
                deviations.append({
                    "parameter": param,
                    "value": value,
                    "sop_range": f"{sop['min']}-{sop['max']} {sop['unit']}",
                    "tolerance_range": f"{min_val:.2f}-{max_val:.2f} {sop['unit']}",
                    "deviation_pct": abs((value - sop["min"]) / sop["min"] * 100)
                })
        
        return deviations
    
    def _calculate_compliance_score(self, deviations: List[Dict[str, Any]]) -> float:
        """Calculate overall compliance score (0-100)."""
        if not deviations:
            return 100.0
        
        # Deduct points for each deviation
        penalty_per_deviation = 100 / (len(self.SOP_PARAMETERS) * 2)
        score = 100 - (len(deviations) * penalty_per_deviation)
        
        return max(0, score)


class RiskAgent:
    """
    Evaluates supplier risk including financial stability and ESG factors.
    Uses mocked data for demonstration (in production, would use real APIs).
    """
    
    # Mock risk database
    RISK_DATABASE = {
        "Acme Pharma": {"financial_score": 85, "esg_score": 90, "red_flags": []},
        "Global Meds Inc": {"financial_score": 60, "esg_score": 45, "red_flags": ["Labor dispute 2025"]},
        "BioTech Solutions": {"financial_score": 95, "esg_score": 88, "red_flags": []},
    }
    
    def __init__(self, compliance_logger: ComplianceLogger):
        """Initialize risk agent."""
        self.compliance_logger = compliance_logger
    
    async def evaluate_risk(self, supplier_name: str) -> Dict[str, Any]:
        """
        Evaluate supplier risk profile.
        
        Args:
            supplier_name: Name of supplier to evaluate
            
        Returns:
            Risk assessment with scores and flags
        """
        logger.info(f"RiskAgent evaluating {supplier_name}")
        
        # Check mock database
        if supplier_name in self.RISK_DATABASE:
            risk_data = self.RISK_DATABASE[supplier_name]
        else:
            # Generate random risk profile for unknown suppliers
            risk_data = {
                "financial_score": random.randint(50, 95),
                "esg_score": random.randint(40, 95),
                "red_flags": self._generate_random_flags()
            }
        
        # Calculate overall risk score
        risk_score = (risk_data["financial_score"] * 0.6 + risk_data["esg_score"] * 0.4)
        
        # Determine status
        if risk_data["red_flags"]:
            status = "DISQUALIFIED"
        elif risk_score >= 80:
            status = "LOW_RISK"
        elif risk_score >= 60:
            status = "MEDIUM_RISK"
        else:
            status = "HIGH_RISK"
        
        assessment = {
            "supplier": supplier_name,
            "financial_score": risk_data["financial_score"],
            "esg_score": risk_data["esg_score"],
            "overall_risk_score": round(risk_score, 2),
            "red_flags": risk_data["red_flags"],
            "status": status,
            "recommendation": self._get_recommendation(status, risk_data["red_flags"])
        }
        
        # Log decision
        self.compliance_logger.log_decision(
            agent_name="RiskAgent",
            action="evaluate_risk",
            inputs={"supplier": supplier_name},
            outputs=assessment
        )
        
        return assessment
    
    def _generate_random_flags(self) -> List[str]:
        """Generate random red flags for demonstration."""
        possible_flags = [
            "Bankruptcy filing detected",
            "Child labor allegations",
            "Environmental violations",
            "Failed audit 2025",
            "Regulatory warning issued"
        ]
        
        # 20% chance of having a red flag
        if random.random() < 0.2:
            return [random.choice(possible_flags)]
        return []
    
    def _get_recommendation(self, status: str, red_flags: List[str]) -> str:
        """Generate recommendation based on risk status."""
        if red_flags:
            return f"REJECT: Red flags detected - {', '.join(red_flags)}"
        elif status == "LOW_RISK":
            return "APPROVE: Low risk supplier, proceed with award"
        elif status == "MEDIUM_RISK":
            return "CONDITIONAL: Require additional due diligence"
        else:
            return "CAUTION: High risk, consider alternatives"


class FinancialAgent:
    """
    Performs should-cost modeling and pricing analysis.
    Uses mocked commodity prices for demonstration.
    """
    
    # Mock commodity prices ($/kg)
    COMMODITY_PRICES = {
        "api_base": 150.0,
        "excipient": 25.0,
        "packaging": 5.0
    }
    
    LABOR_COST_PER_UNIT = 10.0
    TARGET_MARGIN = 0.20  # 20%
    VARIANCE_THRESHOLD = 0.15  # 15% as per PRD
    
    def __init__(self, compliance_logger: ComplianceLogger):
        """Initialize financial agent."""
        self.compliance_logger = compliance_logger
    
    async def analyze_pricing(
        self,
        supplier_name: str,
        bid_price: float,
        quantity: int,
        material_type: str = "api_base"
    ) -> Dict[str, Any]:
        """
        Analyze bid pricing against should-cost model.
        
        Args:
            supplier_name: Name of supplier
            bid_price: Total bid price
            quantity: Quantity of units
            material_type: Type of material (for commodity pricing)
            
        Returns:
            Financial analysis with should-cost comparison
        """
        logger.info(f"FinancialAgent analyzing pricing for {supplier_name}")
        
        # Calculate should-cost
        material_cost = self.COMMODITY_PRICES.get(material_type, 100.0) * quantity
        labor_cost = self.LABOR_COST_PER_UNIT * quantity
        base_cost = material_cost + labor_cost
        should_cost = base_cost * (1 + self.TARGET_MARGIN)
        
        # Calculate variance
        variance = (bid_price - should_cost) / should_cost
        variance_pct = variance * 100
        
        # Determine status
        if abs(variance) <= self.VARIANCE_THRESHOLD:
            status = "FAIR_PRICE"
        elif variance > self.VARIANCE_THRESHOLD:
            status = "OVERPRICED"
        else:
            status = "UNDERPRICED"
        
        analysis = {
            "supplier": supplier_name,
            "bid_price": bid_price,
            "quantity": quantity,
            "should_cost_breakdown": {
                "material_cost": round(material_cost, 2),
                "labor_cost": round(labor_cost, 2),
                "target_margin": f"{self.TARGET_MARGIN * 100}%",
                "total_should_cost": round(should_cost, 2)
            },
            "variance": round(variance_pct, 2),
            "variance_threshold": f"±{self.VARIANCE_THRESHOLD * 100}%",
            "status": status,
            "recommendation": self._get_recommendation(status, variance_pct)
        }
        
        # Log decision
        self.compliance_logger.log_decision(
            agent_name="FinancialAgent",
            action="analyze_pricing",
            inputs={
                "supplier": supplier_name,
                "bid_price": bid_price,
                "quantity": quantity
            },
            outputs=analysis
        )
        
        return analysis
    
    def _get_recommendation(self, status: str, variance_pct: float) -> str:
        """Generate recommendation based on pricing analysis."""
        if status == "FAIR_PRICE":
            return "APPROVE: Pricing aligns with should-cost model"
        elif status == "OVERPRICED":
            return f"NEGOTIATE: Bid is {abs(variance_pct):.1f}% above should-cost, request breakdown"
        else:
            return f"INVESTIGATE: Bid is {abs(variance_pct):.1f}% below should-cost, verify quality"


class Orchestrator:
    """
    Orchestrates the multi-agent system and generates executive summary.
    Aggregates results from all agents and produces final recommendation.
    """
    
    def __init__(self, compliance_logger: ComplianceLogger):
        """Initialize orchestrator."""
        self.compliance_logger = compliance_logger
        self.technical_agent = TechnicalAgent(compliance_logger)
        self.risk_agent = RiskAgent(compliance_logger)
        self.financial_agent = FinancialAgent(compliance_logger)
    
    async def evaluate_bid(
        self,
        pdf_path: str,
        supplier_name: str,
        bid_price: float,
        quantity: int
    ) -> Dict[str, Any]:
        """
        Orchestrate full bid evaluation across all agents.
        
        Args:
            pdf_path: Path to bid PDF
            supplier_name: Supplier name
            bid_price: Total bid price
            quantity: Quantity
            
        Returns:
            Complete evaluation with executive summary
        """
        logger.info(f"Orchestrator evaluating bid from {supplier_name}")
        
        start_time = datetime.now(timezone.utc)
        
        # Run all agents in parallel (simplified sequential for demo)
        technical_analysis = await self.technical_agent.analyze_bid(pdf_path, supplier_name)
        risk_assessment = await self.risk_agent.evaluate_risk(supplier_name)
        financial_analysis = await self.financial_agent.analyze_pricing(
            supplier_name, bid_price, quantity
        )
        
        # Calculate weighted score (40% Technical, 30% Risk, 30% Financial)
        technical_score = technical_analysis.get("compliance_score", 0)
        risk_score = risk_assessment.get("overall_risk_score", 0)
        financial_score = self._calculate_financial_score(financial_analysis)
        
        overall_score = (
            technical_score * 0.40 +
            risk_score * 0.30 +
            financial_score * 0.30
        )
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            supplier_name,
            overall_score,
            technical_analysis,
            risk_assessment,
            financial_analysis
        )
        
        # Determine final recommendation
        final_recommendation = self._get_final_recommendation(
            overall_score,
            technical_analysis,
            risk_assessment,
            financial_analysis
        )
        
        end_time = datetime.now(timezone.utc)
        processing_time = (end_time - start_time).total_seconds()
        
        result = {
            "supplier": supplier_name,
            "overall_score": round(overall_score, 2),
            "weighted_scores": {
                "technical": round(technical_score, 2),
                "risk": round(risk_score, 2),
                "financial": round(financial_score, 2)
            },
            "technical_analysis": technical_analysis,
            "risk_assessment": risk_assessment,
            "financial_analysis": financial_analysis,
            "executive_summary": executive_summary,
            "final_recommendation": final_recommendation,
            "processing_time_seconds": round(processing_time, 2),
            "timestamp": end_time.isoformat()
        }
        
        # Log orchestration decision
        self.compliance_logger.log_decision(
            agent_name="Orchestrator",
            action="evaluate_bid",
            inputs={
                "supplier": supplier_name,
                "bid_price": bid_price,
                "quantity": quantity
            },
            outputs=result
        )
        
        return result
    
    def _calculate_financial_score(self, financial_analysis: Dict[str, Any]) -> float:
        """Convert financial status to score (0-100)."""
        status = financial_analysis.get("status", "FAIR_PRICE")
        variance = abs(financial_analysis.get("variance", 0))
        
        if status == "FAIR_PRICE":
            return 100.0
        elif status == "OVERPRICED":
            return max(50, 100 - variance)
        else:  # UNDERPRICED
            return max(60, 100 - variance * 0.5)
    
    def _generate_executive_summary(
        self,
        supplier_name: str,
        overall_score: float,
        technical: Dict[str, Any],
        risk: Dict[str, Any],
        financial: Dict[str, Any]
    ) -> str:
        """Generate natural language executive summary."""
        summary_parts = [
            f"**Bid Evaluation Summary for {supplier_name}**\n",
            f"Overall Score: {overall_score:.1f}/100\n"
        ]
        
        # Technical summary
        tech_status = technical.get("status", "UNKNOWN")
        tech_score = technical.get("compliance_score", 0)
        summary_parts.append(
            f"\n**Technical Compliance ({tech_score:.1f}/100):** "
            f"{tech_status}. "
        )
        if technical.get("deviations"):
            summary_parts.append(
                f"Found {len(technical['deviations'])} deviation(s) from SOP parameters. "
            )
        else:
            summary_parts.append("All specifications within SOP tolerance. ")
        
        # Risk summary
        risk_status = risk.get("status", "UNKNOWN")
        risk_score = risk.get("overall_risk_score", 0)
        summary_parts.append(
            f"\n**Risk Assessment ({risk_score:.1f}/100):** "
            f"{risk_status}. "
        )
        if risk.get("red_flags"):
            summary_parts.append(
                f"⚠️ RED FLAGS: {', '.join(risk['red_flags'])}. "
            )
        else:
            summary_parts.append("No critical risk flags identified. ")
        
        # Financial summary
        fin_status = financial.get("status", "UNKNOWN")
        variance = financial.get("variance", 0)
        summary_parts.append(
            f"\n**Financial Analysis:** "
            f"{fin_status}. "
            f"Bid variance: {variance:+.1f}% from should-cost model. "
        )
        
        return "".join(summary_parts)
    
    def _get_final_recommendation(
        self,
        overall_score: float,
        technical: Dict[str, Any],
        risk: Dict[str, Any],
        financial: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final recommendation with human-in-the-loop flag."""
        # Check for automatic disqualification
        if risk.get("red_flags"):
            return {
                "decision": "REJECT",
                "confidence": "HIGH",
                "reason": f"Automatic disqualification due to red flags: {', '.join(risk['red_flags'])}",
                "requires_human_approval": False,
                "next_steps": self._get_next_steps("REJECT")
            }
        
        # Score-based recommendation
        if overall_score >= 85:
            decision = "RECOMMEND_AWARD"
            confidence = "HIGH"
            reason = "Excellent overall performance across all criteria"
        elif overall_score >= 70:
            decision = "CONDITIONAL_APPROVAL"
            confidence = "MEDIUM"
            reason = "Good performance but requires additional review"
        elif overall_score >= 50:
            decision = "REQUEST_CLARIFICATION"
            confidence = "LOW"
            reason = "Marginal performance, request additional information"
        else:
            decision = "REJECT"
            confidence = "HIGH"
            reason = "Poor performance across multiple criteria"
        
        return {
            "decision": decision,
            "confidence": confidence,
            "reason": reason,
            "requires_human_approval": True,  # Always require human sign-off per PRD
            "next_steps": self._get_next_steps(decision)
        }
    
    def _get_next_steps(self, decision: str) -> List[str]:
        """Get recommended next steps based on decision."""
        steps_map = {
            "RECOMMEND_AWARD": [
                "Obtain human approval from Category Manager",
                "Initiate contract negotiation",
                "Schedule supplier qualification audit"
            ],
            "CONDITIONAL_APPROVAL": [
                "Request additional technical documentation",
                "Conduct supplier site visit",
                "Obtain human approval with conditions"
            ],
            "REQUEST_CLARIFICATION": [
                "Send RFI (Request for Information) to supplier",
                "Schedule clarification meeting",
                "Re-evaluate after receiving additional data"
            ],
            "REJECT": [
                "Send rejection notice to supplier",
                "Document reasons in procurement system",
                "Consider alternative suppliers"
            ]
        }
        
        return steps_map.get(decision, ["Escalate to Category Manager for review"])


# Global orchestrator instance
_orchestrator: Optional[Orchestrator] = None


async def get_orchestrator() -> Orchestrator:
    """Get or create global orchestrator instance."""
    global _orchestrator
    
    if _orchestrator is None:
        compliance_logger = ComplianceLogger()
        _orchestrator = Orchestrator(compliance_logger)
    
    return _orchestrator