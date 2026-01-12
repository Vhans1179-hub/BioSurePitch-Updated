
# PDF RAG User Guide

**Version:** 1.0
**Last Updated:** January 12, 2026
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Getting Started](#2-getting-started)
3. [Using the PDF RAG Feature](#3-using-the-pdf-rag-feature)
4. [API Reference](#4-api-reference)
5. [Testing Guide](#5-testing-guide)
6. [Troubleshooting](#6-troubleshooting)
7. [Best Practices](#7-best-practices)
8. [Examples](#8-examples)
9. [Limitations and Future Enhancements](#9-limitations-and-future-enhancements)
10. [FAQ](#10-faq)

---

## 📋 Quick Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| Upload PDF | `/api/pdfs/upload` | POST |
| List PDFs | `/api/pdfs/list` | GET |
| Query Documents | `/api/pdfs/query` | POST |
| Sync to Gemini | `/api/pdfs/sync` | POST |
| Delete PDF | `/api/pdfs/{file_name}` | DELETE |
| List Gemini Files | `/api/pdfs/gemini-files` | GET |

**Key Files:**
- Backend Service: [`backend/services/gemini_rag_service.py`](backend/services/gemini_rag_service.py)
- PDF Manager: [`backend/services/pdf_manager.py`](backend/services/pdf_manager.py)
- API Router: [`backend/routers/pdfs.py`](backend/routers/pdfs.py)
- Frontend Component: [`frontend/src/components/chat/PDFManager.tsx`](frontend/src/components/chat/PDFManager.tsx)

---

## 1. Overview

### 1.1 Feature Description

The PDF RAG (Retrieval-Augmented Generation) feature enables AI-powered document search and question-answering across healthcare documents. It leverages Google's Gemini 1.5 Pro with its long context window (up to 2M tokens) to provide accurate, document-grounded responses.

**Key Capabilities:**
- 📄 Upload and manage PDF documents across multiple categories
- 🔍 Intelligent document search and retrieval
- 💬 Natural language querying via chat interface
- 📚 Source citation for all responses
- 🔄 Automatic synchronization with Gemini File API
- 🏥 Healthcare-specific document organization

### 1.2 Use Cases for Healthcare Documents

**Research Papers:**
- Query medical literature and clinical studies
- Find evidence-based treatment protocols
- Access latest research findings

**Clinical Guidelines:**
- Retrieve standard operating procedures
- Access treatment protocols
- Find compliance requirements

**Policies & Contracts:**
- Search insurance policies
- Review contract terms
- Find regulatory requirements

**Clinical Records:**
- Access anonymized patient data (development only)
- Review case studies
- Analyze treatment outcomes

### 1.3 Architecture Summary

The system uses a "Gemini First" approach with future hybrid migration capability:

```
┌─────────────────┐
│  Frontend UI    │
│  (PDFManager)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Router │
│  (pdfs.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  PDF Manager    │◄────►│  Local Storage   │
│  (pdf_manager)  │      │  (backend/data/) │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  RAG Service    │◄────►│  Gemini File API │
│  (gemini_rag)   │      │  (Google Cloud)  │
└─────────────────┘      └──────────────────┘
```

**Design Principles:**
- Service abstraction for future hybrid migration
- Document classification (PUBLIC, INTERNAL, PHI)
- Abstracted querying interface
- HIPAA compliance considerations

For detailed architecture, see [`PDF_RAG_IMPLEMENTATION_PLAN.md`](PDF_RAG_IMPLEMENTATION_PLAN.md).

---

## 2. Getting Started

### 2.1 Prerequisites

**Required:**
- ✅ Python 3.8 or higher
- ✅ Node.js 16+ (for frontend)
- ✅ Google Cloud account with billing enabled
- ✅ Gemini API key (see setup guide)
- ✅ 10GB+ free disk space

**Recommended:**
- 📝 VS Code or similar IDE
- 🐳 Docker (optional, for containerized deployment)
- 📊 Postman or similar API testing tool

### 2.2 Environment Setup Checklist

Follow the comprehensive setup guide: [`GEMINI_SETUP_GUIDE.md`](GEMINI_SETUP_GUIDE.md)

**Quick Checklist:**
- [ ] Google Cloud project created
- [ ] Generative Language API enabled
- [ ] API key generated and secured
- [ ] Billing account linked
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Test script runs successfully

### 2.3 First-Time Configuration

**Step 1: Configure Environment Variables**

Create or update `backend/.env`:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-pro
GEMINI_MAX_TOKENS=8192
GEMINI_TEMPERATURE=0.7

# PDF Storage Configuration
PDF_STORAGE_PATH=backend/data/documents

# File Upload Limits
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf
```

**Step 2: Create Document Directories**

```bash
mkdir -p backend/data/documents/research_papers
mkdir -p backend/data/documents/policies
mkdir -p backend/data/documents/contracts
mkdir -p backend/data/documents/clinical
```

**Step 3: Verify Configuration**

```bash
cd backend
python -c "from config import settings; print(f'API Key configured: {bool(settings.gemini_api_key)}')"
```

### 2.4 Installing Dependencies

**Backend Dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

Key packages:
- `google-generativeai>=0.8.0` - Gemini SDK
- `pypdf` - PDF processing
- `python-multipart` - File uploads
- `fastapi` - API framework
- `uvicorn` - ASGI server

**Frontend Dependencies:**

```bash
cd frontend
npm install
```

**Verify Installation:**

```bash
# Backend
python -c "import google.generativeai as genai; print('Gemini SDK installed')"

# Frontend
npm list react react-dom
```

---

## 3. Using the PDF RAG Feature

### 3.1 Backend Usage

#### 3.1.1 Adding PDFs to the System

**Method 1: Direct File Placement**

Place PDF files in the appropriate category directory:

```bash
# Example: Add a research paper
cp my_research_paper.pdf backend/data/documents/research_papers/

# Example: Add a policy document
cp healthcare_policy.pdf backend/data/documents/policies/
```

Then sync to Gemini:

```bash
curl -X POST http://localhost:8000/api/pdfs/sync
```

**Method 2: API Upload**

```bash
curl -X POST http://localhost:8000/api/pdfs/upload \
  -F "file=@document.pdf" \
  -F "category=research_papers"
```

**Method 3: Python Script**

```python
import requests

url = "http://localhost:8000/api/pdfs/upload"
files = {"file": open("document.pdf", "rb")}
data = {"category": "research_papers"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

#### 3.1.2 Using the API Endpoints

**List All PDFs:**

```bash
# List all PDFs
curl http://localhost:8000/api/pdfs/list

# List PDFs by category
curl http://localhost:8000/api/pdfs/list?category=research_papers
```

**Query Documents:**

```bash
curl -X POST http://localhost:8000/api/pdfs/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the treatment protocols for diabetes?",
    "file_names": null
  }'
```

**Sync PDFs to Gemini:**

```bash
# Sync all categories
curl -X POST http://localhost:8000/api/pdfs/sync

# Sync specific category
curl -X POST "http://localhost:8000/api/pdfs/sync?category=research_papers"

# Force re-upload all files
curl -X POST "http://localhost:8000/api/pdfs/sync?force=true"
```

**Delete a PDF:**

```bash
curl -X DELETE http://localhost:8000/api/pdfs/my_document.pdf
```

**List Gemini Files:**

```bash
curl http://localhost:8000/api/pdfs/gemini-files
```

#### 3.1.3 Service Layer Usage for Developers

**Using the RAG Service:**

```python
from backend.services.gemini_rag_service import get_rag_service

# Initialize service
rag_service = await get_rag_service()

# Upload a PDF
file_name = await rag_service.upload_pdf(
    file_path="path/to/document.pdf",
    display_name="Clinical Guidelines 2024"
)

# Query documents
result = await rag_service.query_documents(
    query="What are the recommended treatments?",
    file_names=None  # Query all documents
)

print(result["response"])
print(result["sources"])

# List uploaded files
files = await rag_service.list_uploaded_files()
for file in files:
    print(f"{file['display_name']}: {file['state']}")

# Delete a file
success = await rag_service.delete_file(file_name)
```

**Using the PDF Manager:**

```python
from backend.services.pdf_manager import get_pdf_manager

pdf_manager = get_pdf_manager()

# Scan local PDFs
pdfs = pdf_manager.scan_local_pdfs(category="research_papers")
for pdf in pdfs:
    print(f"{pdf['display_name']}: {pdf['size_bytes']} bytes")

# Get PDF metadata
metadata = pdf_manager.get_pdf_metadata("path/to/document.pdf")
print(f"Pages: {metadata['num_pages']}")

# Validate PDF
is_valid = pdf_manager.validate_pdf("path/to/document.pdf")

# Sync to Gemini
results = await pdf_manager.sync_pdfs_to_gemini(
    category="research_papers",
    force=False
)
print(f"Uploaded: {results['uploaded']}, Failed: {results['failed']}")
```

#### 3.1.4 Configuration Options

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | (required) | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-1.5-pro` | Model to use |
| `GEMINI_MAX_TOKENS` | `8192` | Maximum response tokens |
| `GEMINI_TEMPERATURE` | `0.7` | Response creativity (0-1) |
| `PDF_STORAGE_PATH` | `backend/data/documents` | Local storage path |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload size |

**Service Configuration:**

```python
# In backend/services/gemini_rag_service.py
class GeminiRAGService:
    def __init__(self):
        self.max_retries = 3  # File processing retries
        self.retry_delay = 2  # Seconds between retries
        self.processing_timeout = 300  # 5 minutes max
```

### 3.2 Frontend Usage

#### 3.2.1 Accessing the Document Library

1. Navigate to the MedAI Agent page
2. Open the chat widget (bottom-right corner)
3. The Document Library is integrated into the chat interface

**Alternative Access:**
- Direct component: Import `PDFManager` from [`frontend/src/components/chat/PDFManager.tsx`](frontend/src/components/chat/PDFManager.tsx)
- Standalone page: Create a dedicated documents page

#### 3.2.2 Uploading PDFs Through the UI

**Step-by-Step:**

1. **Open Document Library**
   - Click the "Document Library" section in the chat widget
   - Or access via dedicated documents page

2. **Select File**
   - Click "Choose File" or drag-and-drop
   - Only `.pdf` files are accepted
   - Maximum size: 10MB (configurable)

3. **Choose Category**
   - Select from dropdown:
     - Research Papers
     - Policies
     - Contracts
     - Clinical

4. **Upload**
   - Click the upload button
   - Wait for confirmation toast
   - File appears in the list with "Processing" status

5. **Verify**
   - Status changes to "Active" when ready
   - Green checkmark indicates successful upload

**Upload Status Indicators:**
- 🟡 **Processing** - File is being processed by Gemini
- 🟢 **Active** - File is ready for queries
- 🔴 **Failed** - Upload or processing failed
- ⚪ **Not Synced** - File exists locally but not in Gemini

#### 3.2.3 Querying Documents via Chat

**Natural Language Queries:**

Simply ask questions in the chat interface. The system automatically searches documents when relevant.

**Example Queries:**

```
"What does the research say about diabetes treatment?"

"Find information about HIPAA compliance in our policies"

"What are the contract terms for hospital partnerships?"

"Show me clinical guidelines for patient care"
```

**Query Indicators:**
- 📚 **Document Search** badge appears on responses
- 🔍 "Searching documents..." animation during processing
- Purple-tinted message bubbles for document responses

**Advanced Queries:**

```
"Compare treatment protocols across all research papers"

"What do our policies say about data privacy?"

"Find all mentions of reimbursement in contracts"

"Summarize the key findings from clinical studies"
```

#### 3.2.4 Managing Documents

**Sync Documents:**
- Click "Sync to Gemini" button
- Uploads any new local files to Gemini
- Updates status for all documents
- Shows sync results in toast notification

**Delete Documents:**
- Click trash icon next to document
- Confirm deletion
- Removes from both local storage and Gemini
- Cannot be undone

**Filter by Category:**
- Use category dropdown
- Select "All Categories" or specific category
- List updates automatically

**View Document Status:**
- File size displayed for each document
- Status badge shows Gemini processing state
- Summary shows total documents and active count

#### 3.2.5 Understanding Source Citations

**Citation Display:**

When the AI responds using documents, sources are displayed at the bottom of the message:

```
📚 Sources:
[Clinical Guidelines 2024] [Research Paper XYZ]
```

**Citation Features:**
- **Clickable badges** - Each source is a clickable badge
- **File identification** - Shows document display name
- **Multiple sources** - Can cite multiple documents per response
- **Transparency** - Always know which documents informed the answer

**Interpreting Citations:**
- More sources = broader research
- Specific source = targeted answer
- No sources = general knowledge response

---

## 4. API Reference

### 4.1 Upload PDF

**Endpoint:** `POST /api/pdfs/upload`

**Description:** Upload a PDF file to local storage and Gemini File API.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (file, required): PDF file to upload
  - `category` (string, required): Document category

**Categories:**
- `research_papers` - Medical journals, clinical studies
- `policies` - Healthcare policies, insurance docs
- `contracts` - Partnership agreements, vendor contracts
- `clinical` - Clinical guidelines, SOPs

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/pdfs/upload \
  -F "file=@clinical_guidelines.pdf" \
  -F "category=clinical"
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "File 'clinical_guidelines.pdf' uploaded successfully",
  "file_metadata": {
    "name": "clinical_guidelines.pdf",
    "display_name": "clinical_guidelines",
    "category": "clinical",
    "size_bytes": 2458624,
    "modified_time": 1705089600.0,
    "hash": "a1b2c3d4...",
    "path": "backend/data/documents/clinical/clinical_guidelines.pdf"
  },
  "gemini_file": {
    "name": "files/abc123xyz",
    "display_name": "clinical_guidelines",
    "mime_type": "application/pdf",
    "size_bytes": 2458624,
    "state": "ACTIVE",
    "uri": "https://generativelanguage.googleapis.com/..."
  }
}
```

**Error Responses:**

| Status | Description |
|--------|-------------|
| 400 | Invalid file type or category |
| 400 | File already exists |
| 400 | Invalid PDF file |
| 500 | Upload failed |

### 4.2 List PDFs

**Endpoint:** `GET /api/pdfs/list`

**Description:** List all uploaded PDFs from local storage.

**Query Parameters:**
- `category` (string, optional): Filter by category

**Example Requests:**

```bash
# List all PDFs
curl http://localhost:8000/api/pdfs/list

# List by category
curl http://localhost:8000/api/pdfs/list?category=research_papers
```

**Response (200 OK):**

```json
{
  "pdfs": [
    {
      "name": "diabetes_study.pdf",
      "display_name": "diabetes_study",
      "category": "research_papers",
      "size_bytes": 1234567,
      "modified_time": 1705089600.0,
      "hash": "e5f6g7h8...",
      "path": "backend/data/documents/research_papers/diabetes_study.pdf"
    }
  ],
  "total": 1,
  "category": "research_papers"
}
```

### 4.3 Query Documents

**Endpoint:** `POST /api/pdfs/query`

**Description:** Query PDFs directly using Gemini RAG.

**Request Body:**

```json
{
  "query": "What are the treatment protocols for diabetes?",
  "file_names": null
}
```

**Parameters:**
- `query` (string, required): Question or search query
- `file_names` (array, optional): Specific Gemini file IDs to query

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/pdfs/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the recommended diabetes treatments?",
    "file_names": null
  }'
```

**Response (200 OK):**

```json
{
  "success": true,
  "response": "According to the clinical guidelines, recommended diabetes treatments include:\n\n1. **Lifestyle Modifications**\n   - Diet control\n   - Regular exercise\n\n2. **Medications**\n   - Metformin as first-line\n   - Insulin therapy for Type 1\n\n3. **Monitoring**\n   - Regular blood glucose checks\n   - HbA1c testing quarterly",
  "sources": [
    {
      "name": "clinical_guidelines",
      "file_id": "files/abc123xyz"
    },
    {
      "name": "diabetes_study",
      "file_id": "files/def456uvw"
    }
  ],
  "error": null
}
```

**Error Response (500):**

```json
{
  "success": false,
  "response": "",
  "sources": [],
  "error": "Failed to query documents: API timeout"
}
```

### 4.4 Sync PDFs

**Endpoint:** `POST /api/pdfs/sync`

**Description:** Sync local PDFs to Gemini File API.

**Query Parameters:**
- `category` (string, optional): Sync specific category only
- `force` (boolean, optional): Re-upload all files (default: false)

**Example Requests:**

```bash
# Sync all categories
curl -X POST http://localhost:8000/api/pdfs/sync

# Sync specific category
curl -X POST "http://localhost:8000/api/pdfs/sync?category=research_papers"

# Force re-upload
curl -X POST "http://localhost:8000/api/pdfs/sync?force=true"
```

**Response (200 OK):**

```json
{
  "uploaded": 3,
  "skipped": 5,
  "failed": 0,
  "errors": [],
  "message": "Sync complete: 3 uploaded, 5 skipped, 0 failed"
}
```

**With Errors:**

```json
{
  "uploaded": 2,
  "skipped": 5,
  "failed": 1,
  "errors": [
    "Failed to upload: corrupted_file.pdf"
  ],
  "message": "Sync complete: 2 uploaded, 5 skipped, 1 failed"
}
```

### 4.5 Delete PDF

**Endpoint:** `DELETE /api/pdfs/{file_name}`

**Description:** Delete a PDF from both local storage and Gemini.

**Path Parameters:**
- `file_name` (string, required): Name of file to delete

**Example Request:**

```bash
curl -X DELETE http://localhost:8000/api/pdfs/old_document.pdf
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "File 'old_document.pdf' deleted from local storage and Gemini",
  "deleted_from_local": true,
  "deleted_from_gemini": true
}
```

**Error Response (404):**

```json
{
  "detail": "File 'nonexistent.pdf' not found in local storage or Gemini"
}
```

### 4.6 List Gemini Files

**Endpoint:** `GET /api/pdfs/gemini-files`

**Description:** List all files uploaded to Gemini File API.

**Example Request:**

```bash
curl http://localhost:8000/api/pdfs/gemini-files
```

**Response (200 OK):**

```json
{
  "files": [
    {
      "name": "files/abc123xyz",
      "display_name": "clinical_guidelines",
      "mime_type": "application/pdf",
      "size_bytes": 2458624,
      "state": "ACTIVE",
      "uri": "https://generativelanguage.googleapis.com/..."
    }
  ],
  "total": 1
}
```

### 4.7 Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters or file |
| 404 | Not Found | Resource not found |
| 413 | Payload Too Large | File exceeds size limit |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error occurred |

### 4.8 Rate Limits

**Free Tier (Gemini API):**
- 15 requests per minute
- 1,500 requests per day
- 1M input tokens per minute
- 10K output tokens per minute

**Recommendations:**
- Implement exponential backoff for 429 errors
- Cache frequently accessed documents
- Batch operations when possible
- Monitor usage in Google Cloud Console

---

## 5. Testing Guide

### 5.1 Manual Testing

#### Test Scenario 1: Upload and Query Workflow

**Objective:** Verify end-to-end PDF upload and query functionality.

**Steps:**

1. **Prepare Test Document**
   ```bash
   # Create a simple test PDF or use existing document
   cp test_document.pdf backend/data/documents/research_papers/
   ```

2. **Upload via API**
   ```bash
   curl -X POST http://localhost:8000/api/pdfs/upload \
     -F "file=@test_document.pdf" \
     -F "category=research_papers"
   ```

3. **Verify Upload**
   ```bash
   curl http://localhost:8000/api/pdfs/list?category=research_papers
   ```

4. **Check Gemini Status**
   ```bash
   curl http://localhost:8000/api/pdfs/gemini-files
   ```

5. **Wait for Processing**
   - Check status until "ACTIVE"
   - May take 30-60 seconds

6. **Query Document**
   ```bash
   curl -X POST http://localhost:8000/api/pdfs/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Summarize this document"}'
   ```

**Expected Results:**
- ✅ Upload returns 200 with file metadata
- ✅ File appears in list
- ✅ Gemini status becomes "ACTIVE"
- ✅ Query returns relevant response with sources

#### Test Scenario 2: Category Filtering

**Objective:** Verify category-based filtering works correctly.

**Steps:**

1. **Upload to Multiple Categories**
   ```bash
   curl -X POST http://localhost:8000/api/pdfs/upload \
     -F "file=@research.pdf" -F "category=research_papers"
   
   curl -X POST http://localhost:8000/api/pdfs/upload \
     -F "file=@policy.pdf" -F "category=policies"
   ```

2. **List All**
   ```bash
   curl http://localhost:8000/api/pdfs/list
   ```

3. **List by Category**
   ```bash
   curl http://localhost:8000/api/pdfs/list?category=research_papers
   curl http://localhost:8000/api/pdfs/list?category=policies
   ```

**Expected Results:**
- ✅ All list shows both files
- ✅ Category filter shows only matching files
- ✅ Total count is correct

#### Test Scenario 3: Sync Operation

**Objective:** Verify sync correctly uploads new files and skips existing ones.

**Steps:**

1. **Add Files Directly**
   ```bash
   cp file1.pdf backend/data/documents/research_papers/
   cp file2.pdf backend/data/documents/research_papers/
   ```

2. **Initial Sync**
   ```bash
   curl -X POST http://localhost:8000/api/pdfs/sync
   ```

3. **Add Another File**
   ```bash
   cp file3.pdf backend/data/documents/research_papers/
   ```

4. **Sync Again**
   ```bash
   curl -X POST http://localhost:8000/api/pdfs/sync
   ```

**Expected Results:**
- ✅ First sync uploads file1 and file2
- ✅ Second sync skips file1 and file2, uploads file3
- ✅ Response shows correct counts

#### Test Scenario 4: Error Handling

**Objective:** Verify proper error handling for invalid inputs.

**Test Cases:**

```bash
# Invalid file type
curl -X POST http://localhost:8000/api/pdfs/upload \
  -F "file=@document.txt" -F "category=research_papers"
# Expected: 400 Bad Request

# Invalid category
curl -X POST http://localhost:8000/api/pdfs/upload \
  -F "file=@document.pdf" -F "category=invalid"
# Expected: 400 Bad Request

# Duplicate file
curl -X POST http://localhost:8000/api/pdfs/upload \
  -F "file=@existing.pdf" -F "category=research_papers"
# Expected: 400 Bad Request (file exists)

# Delete non-existent file
curl -X DELETE http://localhost:8000/api/pdfs/nonexistent.pdf
# Expected: 404 Not Found
```

#### Test Scenario 5: Frontend Integration

**Objective:** Verify UI components work correctly.

**Steps:**

1. **Open Application**
   - Navigate to http://localhost:5173
   - Open chat widget

2. **Upload via UI**
   - Click "Choose File"
   - Select PDF
   - Choose category
   - Click upload button

3. **Verify Upload**
   - Check for success toast
   - Verify file appears in list
   - Check status badge

4. **Query via Chat**
   - Type question about document
   - Send message
   - Verify response includes sources

5. **Delete Document**
   - Click trash icon
   - Confirm deletion
   - Verify file removed

**Expected Results:**
- ✅ Upload shows progress and success
- ✅ File appears with correct status
- ✅ Chat queries return document-based answers
- ✅ Sources displayed correctly
- ✅ Deletion works and updates UI

### 5.2 Automated Testing

#### Unit Tests for PDF Services

Create `backend/tests/test_pdf_services.py`:

```python
import pytest
from pathlib import Path
from backend.services.pdf_manager import PDFManager
from backend.services.gemini_rag_service import GeminiRAGService

@pytest.fixture
def pdf_manager():
    return PDFManager()

@pytest.fixture
def sample_pdf(tmp_path):
    """Create a sample PDF for testing."""
    pdf_path = tmp_path / "test.pdf"
    # Create minimal valid PDF
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF")
    return pdf_path

def test_scan_local_pdfs(pdf_manager):
    """Test scanning local PDF directory."""
    pdfs = pdf_manager.scan_local_pdfs()
    assert isinstance(pdfs, list)

def test_validate_pdf(pdf_manager, sample_pdf):
    """Test PDF validation."""
    is_valid = pdf_manager.validate_pdf(str(sample_pdf))
    assert isinstance(is_valid, bool)

def test_get_file_info(pdf_manager, sample_pdf):
    """Test extracting file information."""
    info = pdf_manager._get_file_info(sample_pdf)
    assert info is not None
    assert "name" in info
    assert "size_bytes" in info
    assert "hash" in info

@pytest.mark.asyncio
async def test_rag_service_initialization():
    """Test RAG service initialization."""
    service = GeminiRAGService()
    # Mock API key for testing
    service.api_key = "test_key"
    # Test initialization logic
    assert service.model_name == "gemini-1.5-pro"
```

#### Integration Tests

Create `backend/tests/test_pdf_integration.py`:

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_list_pdfs_endpoint():
    """Test listing PDFs endpoint."""
    response = client.get("/api/pdfs/list")
    assert response.status_code == 200
    data = response.json()
    assert "pdfs" in data
    assert "total" in data

def test_upload_invalid_file():
    """Test uploading invalid file type."""
    files = {"file": ("test.txt", b"content", "text/plain")}
    data = {"category": "research_papers"}
    response = client.post("/api/pdfs/upload", files=files, data=data)
    assert response.status_code == 400

def test_upload_invalid_category():
    """Test uploading with invalid category."""
    files = {"file": ("test.pdf", b"%PDF-1.4", "application/pdf")}
    data = {"category": "invalid_category"}
    response = client.post("/api/pdfs/upload", files=files, data=data)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_query_endpoint():
    """Test PDF query endpoint."""
    payload = {
        "query": "Test query",
        "file_names": None
    }
    response = client.post("/api/pdfs/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "success" in data
    assert "response" in data
```

#### Running Tests

```bash
# Run all tests
cd backend
pytest

# Run specific test file
pytest tests/test_pdf_services.py

# Run with coverage
pytest --cov=backend.services --cov-report=html

# Run with verbose output
pytest -v
```

### 5.3 Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Upload fails with 400 | Invalid file type | Ensure file is PDF format |
| Processing stuck | Gemini API timeout | Wait 5 minutes, then check status |
| Query returns no results | Documents not synced | Run sync operation |
| 429 Rate limit error | Too many requests | Implement exponential backoff |
| File not found in Gemini | Sync incomplete | Re-run sync with force=true |
| Large file fails | Exceeds size limit | Split PDF or increase limit |

---

## 6. Troubleshooting

### 6.1 Common Errors and Solutions

#### Error: "GEMINI_API_KEY not configured"

**Cause:** API key not set in environment variables.

**Solution:**
```bash
# Check if key is set
echo $GEMINI_API_KEY

# Set in .env file
echo "GEMINI_API_KEY=your_key_here" >> backend/.env

# Restart server
```

#### Error: "File processing timeout"

**Cause:** Large PDF taking too long to process.

**Solution:**
1. Check file size (should be < 10MB)
2. Wait longer (up to 5 minutes)
3. Check Gemini API status
4. Retry upload

```bash
# Check file status
curl http://localhost:8000/api/pdfs/gemini-files

# Re-upload if needed
curl -X POST http://localhost:8000/api/pdfs/sync?force=true
```

#### Error: "Rate limit exceeded (429)"

**Cause:** Too many API requests.

**Solution:**
```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def query_with_retry(query):
    return await rag_service.query_documents(query)
```

#### Error: "Invalid PDF file"

**Cause:** Corrupted or non-standard PDF.

**Solution:**
1. Verify PDF opens in reader
2. Re-export PDF from source
3. Use PDF repair tool
4. Check file integrity

```bash
# Validate PDF
python -c "from pypdf import PdfReader; PdfReader('file.pdf')"
```

### 6.2 Debugging Tips

**Enable Debug Logging:**

```python
# In backend/main.py or config
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Check Service Status:**

```python
from backend.services.gemini_rag_service import get_rag_service

rag_service = await get_rag_service()
print(f"Initialized: {rag_service.initialized}")
print(f"Model: {rag_service.model_name}")
```

**Monitor API Calls:**

```bash
# Watch logs in real-time
tail -f backend/logs/app.log

# Filter for PDF operations
grep "PDF" backend/logs/app.log
```

### 6.3 Logging and Monitoring

**Log Locations:**
- Application logs: `backend/logs/app.log`
- Error logs: `backend/logs/error.log`
- Access logs: `backend/logs/access.log`

**Key Log Messages:**

```
INFO - File uploaded: clinical_guidelines.pdf
INFO - File processing complete: files/abc123xyz
INFO - Query processed: 2 sources used
ERROR - Failed to upload PDF: API timeout
WARNING - Rate limit approaching: 14/15 requests
```

**Monitoring Checklist:**
- [ ] API response times < 2 seconds
- [ ] File processing success rate > 95%
- [ ] Query accuracy validated
- [ ] Storage usage monitored
- [ ] Rate limits tracked

### 6.4 Performance Optimization

**Caching Strategies:**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_query_result(query_hash):
    # Cache frequent queries
    pass
```

**Batch Operations:**

```python
# Upload multiple files efficiently
async def batch_upload(file_paths):
    tasks = [
        rag_service.upload_pdf(path, name)
        for path, name in file_paths
    ]
    return await asyncio.gather(*tasks)
```

**Query Optimization:**

```python
# Query specific files instead of all
result = await rag_service.query_documents(
    query="treatment protocols",
    file_names=["files/abc123", "files/def456"]  # Specific files
)
```

---

## 7. Best Practices

### 7.1 Document Organization Strategies

**Category Guidelines:**

| Category | Use For | Examples |
|----------|---------|----------|
| `research_papers` | Published studies, journals | PubMed articles, clinical trials |
| `policies` | Organizational policies | HIPAA guidelines, privacy policies |
| `contracts` | Legal agreements | Vendor contracts, partnerships |
| `clinical` | Clinical procedures | Treatment protocols, SOPs |

**Naming Conventions:**

```
✅ Good:
- diabetes_treatment_protocol_2024.pdf
- hipaa_compliance_guide_v2.pdf
- vendor_contract_acme_medical.pdf

❌ Avoid:
- document1.pdf
- untitled.pdf
- temp_file.pdf
```

**File Organization:**

```
backend/data/documents/
├── research_papers/
│   ├── cardiology/
│   │   └── heart_disease_study_2024.pdf
│   └── endocrinology/
│       └── diabetes_research_2024.pdf
├── policies/
│   ├── compliance/
│   └── privacy/
└── clinical/
    ├── protocols/
    └── guidelines/
```

### 7.2 Query Optimization Tips

**Effective Query Patterns:**

```
✅ Specific and Clear:
"What are the recommended dosages for metformin in Type 2 diabetes?"

✅ Context-Rich:
"According to our clinical guidelines, what is the protocol for patient intake?"

✅ Comparative:
"Compare treatment outcomes between Protocol A and Protocol B"

❌ Too Vague:
"Tell me about diabetes"

❌ Too Broad:
"What's in the documents?"
```

**Query Best Practices:**

1. **Be Specific:** Include relevant medical terms
2. **Provide Context:** Reference document types
3. **Ask Follow-ups:** Build on previous responses
4. **Use Keywords:** Include technical terminology
5. **Request Citations:** Ask for source references

### 7.3 Security Considerations

**API Key Security:**

```bash
# ✅ Use environment variables
export GEMINI_API_KEY="your_key"

# ✅ Use .env files (not committed)
echo "GEMINI_API_KEY=key" > .env

# ❌ Never hardcode
api_key = "AIzaSy..."  # DON'T DO THIS
```

**Access Control:**

```python
# Implement role-based access
from fastapi import Depends, HTTPException

async def verify_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403)
    return user

@router.post("/pdfs/upload")
async def upload_pdf(admin: User = Depends(verify_admin)):
    # Only admins can upload
    pass
```

**Data Sanitization:**

```python
# Sanitize file names
import re

def sanitize_filename(filename: str) -> str:
    # Remove special characters
    clean = re.sub(r'[^\w\s.-]', '', filename)
    # Limit length
    return clean[:255]
```

### 7.4 HIPAA Compliance Reminders

**⚠️ CRITICAL: PHI Handling**

**Development Environment:**
- ✅ Use synthetic/anonymized data only
- ✅ No real patient information
- ✅ Test with mock data

**Production Environment:**
- ✅ Requires Google Cloud BAA
- ✅ Enterprise tier Gemini API
- ✅ Audit logging enabled
- ✅ Encryption at rest and in transit
- ✅ Access controls implemented

**Compliance Checklist:**

```
Before uploading ANY document with PHI:
[ ] BAA signed with Google Cloud
[ ] Enterprise tier activated
[ ] Document classification reviewed
[ ] Access controls verified
[ ] Audit logging enabled
[ ] Encryption confirmed
[ ] Staff training completed
[ ] Incident response plan ready
```

**Document Classification:**

```python
# Tag documents appropriately
class DocumentClassification:
    PUBLIC = "public"        # No PHI, can use standard API
    INTERNAL = "internal"    # Business sensitive, standard API OK
    PHI = "phi"             # Contains PHI, requires BAA + Enterprise
```

---

## 8. Examples

### 8.1 Real-World Usage Examples

#### Example 1: Clinical Research Query

**Scenario:** Physician wants to find treatment protocols for diabetes.

**Query:**
```
"What are the latest evidence-based treatment protocols for Type 2 diabetes according to our research papers?"
```

**Expected Response:**
```
According to the clinical research papers in our database:

**First-Line Treatment:**
1. Metformin 500-2000mg daily
2. Lifestyle modifications (diet + exercise)

**Second-Line Options:**
- GLP-1 receptor agonists
- SGLT2 inhibitors
- DPP-4 inhibitors

**Monitoring:**
- HbA1c every 3 months
- Annual comprehensive metabolic panel

📚 Sources:
[Diabetes Treatment Guidelines 2024] [ADA Standards of Care 2024]
```

#### Example 2: Policy Compliance Check

**Scenario:** Compliance officer needs HIPAA requirements.

**Query:**
```
"What are our organization's requirements for handling patient data according to HIPAA policies?"
```

**Expected Response:**
```
Based on our HIPAA compliance policies:

**Data Handling Requirements:**
1. Encryption at rest and in transit
2. Access controls with role-based permissions
3. Audit logging of all PHI access
4. Regular security assessments

**Staff Requirements:**
- Annual HIPAA training mandatory
- Signed confidentiality agreements
- Background checks completed

**Breach Protocol:**
- Report within 24 hours
- Document incident details
- Notify affected parties per timeline

📚 Sources:
[HIPAA Compliance Guide v2.1] [Data Privacy Policy 2024]
```

#### Example 3: Contract Review

**Scenario:** Legal team reviewing vendor contract terms.

**Query:**
```
"What are the payment terms and SLA commitments in the Acme Medical vendor contract?"
```

**Expected Response:**
```
From the Acme Medical vendor contract:

**Payment Terms:**
- Net 30 days from invoice date
- 2% early payment discount if paid within 10 days
- Late payment penalty: 1.5% per month

**SLA Commitments:**
- 99.9% uptime guarantee
- < 2 hour response time for critical issues
- < 24 hour resolution for non-critical issues
- Monthly performance reports

**Penalties for SLA Breach:**
- 5% credit for each 0.1% below 99.9% uptime
- Maximum credit: 25% of monthly fees

📚 Sources:
[Acme Medical Vendor Contract 2024]
```

### 8.2 Sample Queries and Expected Responses

**Medical Research:**
```
Q: "Summarize the key findings from cardiovascular research papers"
A: [Comprehensive summary with citations]

Q: "What are the contraindications for ACE inhibitors?"
A: [Detailed list with source references]

Q: "Compare efficacy rates between Drug A and Drug B"
A: [Comparative analysis with statistics]
```

**Clinical Guidelines:**
```
Q: "What is the protocol for emergency triage?"
A: [Step-by-step protocol with priority levels]

Q: "Show me the infection control procedures"
A: [Detailed procedures with compliance notes]

Q: "What are the documentation requirements for procedures?"
A: [Requirements list with examples]
```

**Policy Questions:**
```
Q: "What is our data retention policy?"
A: [Retention periods and procedures]

Q: "Who has access to patient records?"
A: [Access control matrix]

Q: "What is the process for patient consent?"
A: [Consent workflow and requirements]
```

### 8.3 Integration Examples

#### Integration with Chat System

```python
# In backend/services/chat_handlers.py
from backend.services.gemini_rag_service import get_rag_service

class PDFKnowledgeHandler:
    async def handle(self, message: str, context: dict):
        # Detect if query needs document search
        if self.needs_document_search(message):
            rag_service = await get_rag_service()
            result = await rag_service.query_documents(message)
            
            return {
                "response": result["response"],
                "sources": result["sources"],
                "type": "pdf_response"
            }
```

#### Integration with External Systems

```python
# Webhook for document updates
@router.post("/webhooks/document-updated")
async def document_updated_webhook(payload: dict):
    """Trigger sync when documents are updated externally."""
    pdf_manager = get_pdf_manager()
    results = await pdf_manager.sync_pdfs_to_gemini()
    return {"status": "synced", "results": results}
```

#### Scheduled Sync Job

```python
# Using APScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=2)  # Run at 2 AM daily
async def scheduled_sync():
    """Sync documents daily."""
    pdf_manager = get_pdf_manager()
    results = await pdf_manager.sync_pdfs_to_gemini()
    logger.info(f"Scheduled sync complete: {results}")

scheduler.start()
```

---

## 9. Limitations and Future Enhancements

### 9.1 Current Limitations

**Technical Limitations:**
- Maximum file size: 10MB (configurable)
- Processing time: Up to 5 minutes for large files
- Rate limits: 15 requests/minute (free tier)
- Context window: 2M tokens (Gemini 1.5 Pro)
- File formats: PDF only (no DOCX, images, etc.)

**Functional Limitations:**
- No OCR for scanned PDFs
- No image extraction from PDFs
- No table structure preservation
- No multi-language support (English optimized)
- No version control for documents

**HIPAA Limitations:**
- Free tier NOT HIPAA compliant
- Requires Enterprise tier + BAA for PHI
- No local-only processing option (yet)

### 9.2 Roadmap for Hybrid Approach

**Phase 1: Enhanced Gemini Integration** (Current)
- ✅ Basic PDF upload and query
- ✅ Source citations
- ✅ Category organization
- ✅ Sync operations

**Phase 2: Local Vector Database** (Q2 2026)
- 🔄 ChromaDB integration
- 🔄 Local embeddings generation
- 🔄 Hybrid query routing
- 🔄 PHI-safe local processing

**Phase 3: Advanced Features** (Q3 2026)
- 📅 OCR for scanned documents
- 📅 Multi-format support (DOCX, images)
- 📅 Document versioning
- 📅 Advanced search filters

**Phase 4: Enterprise Features** (Q4 2026)
- 📅 Multi-tenant support
- 📅 Advanced access controls
- 📅 Compliance reporting
- 📅 Custom model fine-tuning

### 9.3 Known Issues

| Issue | Impact | Workaround | ETA Fix |
|-------|--------|------------|---------|
| Large PDFs timeout | Medium | Split into smaller files | Q2 2026 |
| Scanned PDFs not searchable | High | Use OCR pre-processing | Q2 2026 |
| No table extraction | Low | Manual table entry | Q3 2026 |
| Rate limit on free tier | Medium | Upgrade to paid tier | N/A |

**Report Issues:**
- GitHub: [Project Issues](https://github.com/your-repo/issues)
- Email: support@yourcompany.com
- Slack: #pdf-rag-support

---

## 10. FAQ

### General Questions

**Q: What file formats are supported?**  
A: Currently only PDF files are supported. DOCX and image support planned for Q3 2026.

**Q: How large can my PDF files be?**  
A: Default limit is 10MB. This can be increased in configuration, but larger files take longer to process.

**Q: How long does it take to process a PDF?**  
A: Small files (< 1MB): 10-30 seconds. Large files (5-10MB): 1-5 minutes.

**Q: Can I upload scanned PDFs?**  
A: Yes, but text extraction may be limited. OCR support coming in Q2 2026.

### Technical Questions

**Q: Where are my PDFs stored?**  
A: Locally in `backend/data/documents/` and uploaded to Gemini File API for processing.

**Q: Can I delete files from Gemini without deleting locally?**  
A: Not through the UI, but you can use the Gemini API directly to delete specific files.

**Q: How do I query specific documents only?**  
A: Use the `file_names` parameter in the query API with specific Gemini file IDs.

**Q: Can I use this offline?**  
A: No, Gemini API requires internet connection. Local-only mode planned for Phase 2.

### Security & Compliance

**Q: Is this HIPAA compliant?**  
A: Only with Enterprise tier Gemini API + signed BAA. Free tier is NOT HIPAA compliant.

**Q: Can I use this with real patient data?**  
A: Only in production with proper BAA and Enterprise tier. Use synthetic data for development.

**Q: How is my API key secured?**  
A: Stored in environment variables, never committed to git. Follow security best practices in Section 7.3.

**Q: Are my documents encrypted?**  
A: Yes, encrypted in transit (HTTPS) and at rest (Google Cloud default encryption).

### Usage Questions

**Q: How do I know which documents were used for a response?**  
A: Check the "Sources" section at the bottom of each AI response.

**Q: Can I search across all categories at once?**  
A: Yes, by default queries search all uploaded documents. Use category filters for specific searches.

**Q: What happens if I upload a duplicate file?**  
A: The system will reject it with a 400 error. Delete the old file first or rename the new one.

**Q: How do I update an existing document?**  
A: Delete the old version and upload the new one. Version control coming in Phase 3.

### Troubleshooting

**Q: My upload is stuck at "Processing"**  
A: Wait up to 5 minutes. If still stuck, check Gemini API status and retry.

**Q: I'm getting rate limit errors**  
A: You've exceeded 15 requests/minute. Wait or upgrade to paid tier for higher limits.

**Q: Queries return irrelevant results**  
A: Try more specific queries with medical terminology. Check that relevant documents are uploaded and synced.

**Q: How do I reset everything?**  
A: Delete all files from `backend/data/documents/` and run sync to clear Gemini storage.

---

## Additional Resources

### Documentation Links
- [PDF RAG Implementation Plan](PDF_RAG_IMPLEMENTATION_PLAN.md)
- [Gemini Setup Guide](GEMINI_SETUP_GUIDE.md)
- [Backend API Documentation](backend/README.md)
- [Frontend Component Guide](frontend/README.md)

### External Resources
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Gemini Python SDK](https://ai.google.dev/api/python/google/generativeai)
- [HIPAA Compliance Guide](https://cloud.google.com/security/compliance/hipaa)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Support Channels
- **Technical Support:** support@yourcompany.com
- **Bug Reports:** GitHub Issues
- **Feature Requests:** GitHub Discussions
- **Community:** Slack #pdf-rag-support

---

## Changelog

### Version 1.0 (2026-01-12)
- Initial release of PDF RAG feature
- Gemini File API integration
- Basic upload, query, and management
- Frontend UI components
- Comprehensive documentation

---

**Document Maintained By:** Development Team  
**Last Review Date:** January 12, 2026  
**Next Review Date:** April 12, 2026

---

*For questions or feedback about this documentation, please contact the development team or open an issue on GitHub.*
