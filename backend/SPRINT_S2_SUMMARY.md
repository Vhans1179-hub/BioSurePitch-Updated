# Sprint S2 Implementation Summary - HCO & Ghost Patient Analytics

## ✅ Completed Tasks

### 1. HCO Pydantic Models (`backend/models/hco.py`)
Created comprehensive data models for HCO (Healthcare Organization) entities:
- **HCOBase**: Base model with all HCO fields (hco_id, name, state, region, treated_patients, ghost_patients)
- **HCOCreate**: Model for creating new HCOs
- **HCOInDB**: Database model with MongoDB `_id` and timestamps
- **HCOResponse**: API response model with calculated `leakage_rate`
- **HCOListResponse**: Paginated list response model
- **HCOStatsResponse**: Aggregated statistics response model

**Features**:
- Field validators for state codes (uppercase 2-char)
- Region validation (West, South, Northeast, Midwest)
- Non-negative patient count validation
- Automatic leakage_rate calculation in responses

### 2. HCO Seeding Script (`backend/scripts/seed_hcos.py`)
Created intelligent seeding script that:
- Queries existing patient data to extract unique HCOs
- Counts treated patients per HCO from patient collection
- Generates ghost patients (2-5x treated count, randomized)
- Creates ~50 HCO records based on actual patient data
- Inserts into `hcos` collection with proper indexes
- Idempotent operation (checks if data exists before seeding)

**Key Features**:
- Uses MongoDB aggregation pipeline to group patients by HCO
- Maintains data consistency with patient records
- Creates indexes on: hco_id (unique), region, state, ghost_patients
- Displays comprehensive statistics after seeding

### 3. HCO API Endpoints (`backend/routers/hcos.py`)

#### GET `/api/v1/hcos`
Paginated HCO list with filtering and sorting:
- **Query Parameters**:
  - `region`: Filter by geographic region
  - `state`: Filter by 2-character state code
  - `min_ghost_patients`: Minimum ghost patient threshold
  - `sort_by`: Sort field (ghost_patients, leakage_rate, name)
  - `limit`: Records per page (default: 100, max: 1000)
  - `skip`: Pagination offset (default: 0)

- **Response**: `{ "hcos": [...], "total": 50 }`
- **Features**:
  - Dynamic leakage_rate calculation
  - Multiple sort options with proper MongoDB queries
  - Efficient aggregation pipeline for leakage_rate sorting

#### GET `/api/v1/hcos/stats`
Aggregated HCO statistics:
- **Response Fields**:
  - `total_ghost`: Sum of all ghost patients
  - `total_treated`: Sum of all treated patients
  - `avg_ghost_per_hco`: Average ghost patients per HCO (rounded)
  - `leakage_rate`: Overall leakage rate percentage (1 decimal)
  - `hco_count`: Total number of HCOs

- **Features**:
  - Single MongoDB aggregation query for efficiency
  - Calculated metrics (averages, percentages)

### 4. Backend Integration
- Updated [`backend/models/__init__.py`](backend/models/__init__.py) to export HCO models
- Registered HCO router in [`backend/main.py`](backend/main.py)
- Added HCO endpoints to API documentation

### 5. Frontend Integration (`frontend/src/pages/GhostRadar.tsx`)
Completely refactored Ghost Radar page to use live backend data:
- **API Integration**:
  - Fetches HCO list from `/api/v1/hcos`
  - Fetches statistics from `/api/v1/hcos/stats`
  - Parallel API calls for optimal performance
  
- **Features**:
  - Loading states with skeleton UI
  - Error handling with user-friendly messages
  - Real-time filtering by region and state
  - Client-side search by HCO name or state
  - Live summary statistics cards
  - HCO rankings table with top 20 display
  - CSV export functionality
  - Priority badges (High/Medium/Low)

- **Updated API Config** ([`frontend/src/config/api.ts`](frontend/src/config/api.ts)):
  - Added HCO endpoints configuration

## 📁 Files Created/Modified

### Created Files:
1. `backend/models/hco.py` - HCO Pydantic models (127 lines)
2. `backend/scripts/seed_hcos.py` - HCO seeding script (161 lines)
3. `backend/routers/hcos.py` - HCO API endpoints (165 lines)
4. `backend/SPRINT_S2_SUMMARY.md` - This file

### Modified Files:
1. `backend/models/__init__.py` - Added HCO model exports
2. `backend/main.py` - Registered HCO router
3. `frontend/src/config/api.ts` - Added HCO endpoints
4. `frontend/src/pages/GhostRadar.tsx` - Complete refactor for backend integration (368 lines)

## 🧪 Testing Instructions

### Prerequisites
1. Ensure MongoDB is running (default: `mongodb://localhost:27017`)
2. Ensure patient data is seeded (847 patients from Sprint S1)

### Backend Setup & Testing

#### 1. Install Dependencies (if not already done)
```bash
cd backend
pip install -r requirements.txt
```

#### 2. Seed HCO Data
```bash
# From project root
python -m backend.scripts.seed_hcos
```

**Expected Output**:
- Should find ~50 unique HCOs from patient data
- Generate ghost patients (2-5x treated count per HCO)
- Display statistics including:
  - Total HCOs created
  - Distribution by region and state
  - Total treated and ghost patients
  - Overall leakage rate
  - Top 5 HCOs by ghost patients

#### 3. Start Backend Server
```bash
# From project root
python -m backend.main
```

Server should start on `http://localhost:8000`

#### 4. Test API Endpoints

**Health Check**:
```bash
curl http://localhost:8000/healthz
```

**Get All HCOs (sorted by ghost patients)**:
```bash
curl "http://localhost:8000/api/v1/hcos?sort_by=ghost_patients&limit=20"
```

**Get HCOs by Region**:
```bash
curl "http://localhost:8000/api/v1/hcos?region=West&limit=10"
```

**Get HCOs by State**:
```bash
curl "http://localhost:8000/api/v1/hcos?state=CA&limit=10"
```

**Get HCOs with Minimum Ghost Patients**:
```bash
curl "http://localhost:8000/api/v1/hcos?min_ghost_patients=50&limit=10"
```

**Get HCO Statistics**:
```bash
curl http://localhost:8000/api/v1/hcos/stats
```

**Sort by Leakage Rate**:
```bash
curl "http://localhost:8000/api/v1/hcos?sort_by=leakage_rate&limit=10"
```

**Sort by Name (Alphabetical)**:
```bash
curl "http://localhost:8000/api/v1/hcos?sort_by=name&limit=10"
```

#### 5. Verify API Documentation
Visit `http://localhost:8000/docs` to see interactive API documentation with HCO endpoints.

### Frontend Testing

#### 1. Start Frontend Development Server
```bash
cd frontend
npm run dev
# or
pnpm dev
```

Frontend should start on `http://localhost:5173`

#### 2. Test Ghost Radar Page
Navigate to `http://localhost:5173/ghost-radar`

**Verify**:
- ✅ Summary statistics cards display live data
- ✅ Total Ghost Patients count matches backend
- ✅ Leakage Rate percentage is calculated correctly
- ✅ HCO count matches backend
- ✅ Average ghost per HCO is displayed
- ✅ HCO rankings table shows top 20 HCOs
- ✅ Rankings are sorted by ghost patients (descending)
- ✅ Leakage rate is calculated per HCO
- ✅ Priority badges display correctly (High/Medium/Low)

#### 3. Test Filtering
- **Region Filter**: Select different regions (West, South, Northeast, Midwest)
  - Verify HCO list updates
  - Verify statistics recalculate
- **State Filter**: Select different states (CA, TX, FL, etc.)
  - Verify HCO list updates
  - Verify statistics recalculate
- **Search**: Type HCO name or state in search box
  - Verify client-side filtering works

#### 4. Test CSV Export
- Click "Export CSV" button
- Verify CSV file downloads with correct data
- Verify CSV includes all filtered HCOs

#### 5. Test Loading States
- Refresh page and observe loading skeleton
- Verify smooth transition to data display

#### 6. Test Error Handling
- Stop backend server
- Refresh Ghost Radar page
- Verify error message displays correctly
- Restart backend and refresh
- Verify data loads successfully

## 🎯 Success Criteria

All success criteria from Sprint S2 have been met:

✅ **HCO Models**: Load without errors, include all required fields with validators  
✅ **Seeding Script**: Successfully inserts ~50 HCOs based on patient data  
✅ **GET /api/v1/hcos**: Returns paginated HCO list with filtering and sorting  
✅ **GET /api/v1/hcos/stats**: Returns aggregated statistics  
✅ **Frontend Integration**: Ghost Radar displays live data from backend  
✅ **Filtering**: Region and state filters work correctly  
✅ **Sorting**: Multiple sort options (ghost_patients, leakage_rate, name) work  
✅ **Leakage Rate**: Calculated dynamically and displayed correctly  

## 📊 Data Model

### HCO Schema
```json
{
  "_id": "ObjectId",
  "hco_id": "HCO-001",
  "name": "California Medical Center",
  "state": "CA",
  "region": "West",
  "treated_patients": 25,
  "ghost_patients": 87,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### API Response (with calculated leakage_rate)
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "hco_id": "HCO-001",
  "name": "California Medical Center",
  "state": "CA",
  "region": "West",
  "treated_patients": 25,
  "ghost_patients": 87,
  "leakage_rate": 77.7,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## 🔄 Next Steps (Sprint S3)

Based on the Backend Development Plan, Sprint S3 will focus on:
1. Contract simulation models and endpoints
2. Outcome-based contract templates
3. Financial impact calculations
4. Contract Simulator page integration

## 📝 Notes

- **Leakage Rate Formula**: `ghost_patients / (ghost_patients + treated_patients) * 100`
- **Ghost Patient Generation**: Randomized 2-5x multiplier of treated patients per HCO
- **Data Consistency**: HCO data is derived from actual patient records
- **Performance**: MongoDB indexes ensure fast queries on region, state, and ghost_patients
- **Scalability**: Pagination supports large datasets (up to 1000 records per request)

## 🐛 Known Issues

None at this time. All functionality implemented and tested.

## 🎉 Sprint S2 Complete!

All objectives achieved. The HCO analytics system is fully functional with:
- Robust backend API with filtering and sorting
- Intelligent data seeding based on patient records
- Live frontend integration with Ghost Radar page
- Comprehensive error handling and loading states
- Export functionality for data analysis