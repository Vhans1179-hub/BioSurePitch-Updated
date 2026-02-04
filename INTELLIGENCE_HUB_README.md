# Intelligence Hub - Multi-Agent Bid Evaluation System

## Overview

The **Intelligence Hub** is a simplified multi-agent system (MAS) designed to automate pharmaceutical bid evaluation. It implements the core concepts from the PRD while using mocked data sources for demonstration purposes.

## Architecture

### Multi-Agent System Components

#### 1. **TechnicalAgent** (`backend/services/procurement_agents.py`)
- **Purpose**: Analyzes technical specifications from bid PDFs
- **Implementation**: 
  - Uses Gemini RAG to extract technical parameters from PDF documents
  - Compares extracted specs against predefined SOP parameters
  - Flags deviations beyond ±5% tolerance
  - Calculates compliance score (0-100)
- **Mock Data**: SOP parameters are hardcoded for demonstration

#### 2. **RiskAgent** (`backend/services/procurement_agents.py`)
- **Purpose**: Evaluates supplier risk (financial, ESG, red flags)
- **Implementation**:
  - Checks mock risk database for known suppliers
  - Generates random risk profiles for unknown suppliers
  - Identifies red flags (bankruptcy, labor issues, etc.)
  - Calculates weighted risk score (60% financial, 40% ESG)
- **Mock Data**: All risk data is simulated (no real API calls)

#### 3. **FinancialAgent** (`backend/services/procurement_agents.py`)
- **Purpose**: Performs should-cost modeling and pricing analysis
- **Implementation**:
  - Uses fixed commodity prices for materials
  - Calculates should-cost: `(Material × Qty) + (Labor × Qty) × (1 + Margin)`
  - Compares bid price against should-cost model
  - Flags variances exceeding ±15% threshold
- **Mock Data**: Commodity prices are hardcoded constants

#### 4. **Orchestrator** (`backend/services/procurement_agents.py`)
- **Purpose**: Coordinates all agents and generates final recommendation
- **Implementation**:
  - Runs all three agents sequentially
  - Aggregates scores with weighted formula: 40% Technical + 30% Risk + 30% Financial
  - Generates natural language executive summary
  - Produces final recommendation with next steps
  - Enforces human-in-the-loop approval requirement

#### 5. **ComplianceLogger** (`backend/services/procurement_agents.py`)
- **Purpose**: Maintains immutable audit trail for GxP compliance
- **Implementation**:
  - Logs all agent decisions to append-only JSONL files
  - Captures: timestamp, agent, action, inputs, outputs, user
  - Supports 21 CFR Part 11 traceability requirements
  - Stores logs in `backend/data/audit_logs/`

## API Endpoints

### POST `/api/v1/procurement/analyze-bid`

Analyzes a pharmaceutical bid using the multi-agent system.

**Request (multipart/form-data):**
```
file: PDF file (required)
supplier_name: string (required)
bid_price: float (required, > 0)
quantity: integer (required, > 0)
material_type: string (optional, default: "api_base")
```

**Response:**
```json
{
  "success": true,
  "supplier": "Acme Pharma",
  "overall_score": 87.5,
  "weighted_scores": {
    "technical": 95.0,
    "risk": 85.0,
    "financial": 80.0
  },
  "technical_analysis": { ... },
  "risk_assessment": { ... },
  "financial_analysis": { ... },
  "executive_summary": "...",
  "final_recommendation": {
    "decision": "RECOMMEND_AWARD",
    "confidence": "HIGH",
    "reason": "...",
    "requires_human_approval": true,
    "next_steps": [...]
  },
  "processing_time_seconds": 12.5,
  "timestamp": "2026-01-29T16:00:00Z"
}
```

### GET `/api/v1/procurement/health`

Health check endpoint for the Intelligence Hub service.

## Frontend Interface

### Intelligence Hub Page (`/intelligence-hub`)

**Features:**
- PDF file upload for bid documents
- Form inputs for supplier details (name, price, quantity, material type)
- Real-time analysis with loading states
- Comprehensive results display:
  - Overall score with weighted breakdown
  - Executive summary
  - Final recommendation with next steps
  - Detailed agent analysis tabs (Technical, Risk, Financial)
  - Visual indicators (progress bars, badges, color coding)

**Access:** Navigate to `http://localhost:5173/intelligence-hub`

## Key Features Implemented

### ✅ From PRD Requirements

1. **Multi-Agent Architecture**: Orchestrator pattern with specialized agents
2. **Technical Analysis**: PDF extraction + SOP comparison with ±5% tolerance
3. **Risk Evaluation**: Financial + ESG scoring with red flag detection
4. **Financial Modeling**: Should-cost calculation with 15% variance threshold
5. **Weighted Scoring**: 40% Technical, 30% Risk, 30% Financial
6. **Executive Summary**: Natural language synthesis of all findings
7. **Compliance Logging**: Immutable audit trail for GxP/21 CFR Part 11
8. **Human-in-the-Loop**: All recommendations require human approval

### 🔄 Simplified/Mocked Components

1. **External APIs**: Bloomberg, Reuters, EcoVadis → Mocked data
2. **Commodity Prices**: LME, ICIS → Fixed constants
3. **Adverse Media**: Web scraping → Random/fixed flags
4. **Technical Extraction**: Full NLP → Gemini + mock parsing

## Installation & Setup

### Backend Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
# Create .env file with:
GEMINI_API_KEY=your_api_key_here
```

3. **Create audit log directory:**
```bash
mkdir -p backend/data/audit_logs
```

4. **Run backend:**
```bash
cd backend
python main.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Run frontend:**
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Usage Example

1. Navigate to `http://localhost:5173/intelligence-hub`
2. Upload a pharmaceutical bid PDF
3. Enter supplier details:
   - Supplier Name: "Acme Pharma"
   - Bid Price: 150000
   - Quantity: 1000
   - Material Type: API Base
4. Click "Analyze Bid"
5. Review results:
   - Overall score and weighted breakdown
   - Executive summary
   - Final recommendation
   - Detailed agent analysis in tabs

## Compliance & Audit Trail

All agent decisions are logged to:
```
backend/data/audit_logs/YYYYMMDD_audit.jsonl
```

Each log entry contains:
- Unique log ID
- Timestamp (UTC)
- Agent name
- Action performed
- Input parameters
- Output results
- User identifier

## Success Metrics (from PRD)

The system is designed to support:

1. **Efficiency**: Reduce time-to-award from 45 days to 14 days
   - Current processing time: ~10-15 seconds per bid
   
2. **Risk Mitigation**: 0% emergency onboarding due to missed signals
   - Red flag detection with automatic disqualification
   
3. **Cost Optimization**: >95% alignment with should-cost models
   - 15% variance threshold with negotiation triggers

## Future Enhancements

To move from demo to production:

1. **Replace Mock Data Sources:**
   - Integrate real Bloomberg/Reuters APIs for financial data
   - Connect to EcoVadis for ESG scores
   - Implement web scraping for adverse media
   - Use real commodity price feeds (LME, ICIS)

2. **Enhanced Technical Analysis:**
   - Structured output from Gemini for reliable parsing
   - Custom NLP models for pharmaceutical specifications
   - Integration with internal SOP databases

3. **Advanced Features:**
   - Parallel agent execution for faster processing
   - Machine learning for should-cost prediction
   - Historical bid analysis and benchmarking
   - Supplier performance tracking over time

4. **Enterprise Integration:**
   - SSO/authentication
   - Role-based access control
   - Integration with procurement systems (SAP, Oracle)
   - Advanced reporting and analytics

## Technical Stack

**Backend:**
- FastAPI (Python web framework)
- Google Gemini (AI/RAG for PDF analysis)
- Pydantic (data validation)
- Motor (async MongoDB - for future use)

**Frontend:**
- React + TypeScript
- Tailwind CSS + shadcn/ui components
- Vite (build tool)

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support & Troubleshooting

**Common Issues:**

1. **"Failed to analyze bid"**
   - Ensure backend is running on port 8000
   - Check GEMINI_API_KEY is configured
   - Verify PDF file is valid

2. **"Service not initialized"**
   - Restart backend server
   - Check Gemini API key validity

3. **Slow processing**
   - First analysis may take longer (Gemini file upload)
   - Subsequent analyses are faster

## License

This is a demonstration implementation for the Intelligence Hub PRD.