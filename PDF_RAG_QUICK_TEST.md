# PDF RAG Quick Test Guide

This guide will help you test the PDF RAG (Retrieval-Augmented Generation) implementation with your uploaded research paper.

## Prerequisites

✅ Backend running at http://localhost:8000
✅ Frontend running at http://localhost:5137
✅ PDF file uploaded to `backend/data/documents/research_papers/`
✅ Gemini API key configured in backend/.env

---

## Option 1: Test via Frontend UI (Recommended)

### Step 1: Access the Chat Interface
1. Open your browser to http://localhost:5137
2. Navigate to the chat interface (look for chat widget or AI assistant)

### Step 2: Upload/Sync the PDF
1. Look for the PDF Manager or document upload section in the chat interface
2. You should see your uploaded PDF listed
3. Click "Sync to Gemini" or similar button to upload the PDF to Gemini's File API
4. Wait for the sync to complete (you'll see a success message)

**Expected Result:**
- Status changes from "Not Synced" to "Processing" to "Active"
- You'll see a confirmation message when ready

### Step 3: Query the Document
Try these sample queries:

**General Understanding:**
```
What is this research paper about?
```

**Specific Details:**
```
What methodology was used in this study?
```

**Data Extraction:**
```
What were the main findings or results?
```

**Citation Test:**
```
Can you quote the abstract or introduction?
```

### Step 4: Verify the Response
Check that the response includes:
- ✅ Relevant answer to your question
- ✅ Source citations showing which PDF was used
- ✅ Page numbers or section references (if available)

---

## Option 2: Test via API (curl commands)

### Step 1: Check PDF Upload Status
```bash
curl http://localhost:8000/api/pdfs
```

**Expected Response:**
```json
{
  "pdfs": [
    {
      "filename": "your-research-paper.pdf",
      "category": "research_papers",
      "file_path": "backend/data/documents/research_papers/your-research-paper.pdf",
      "gemini_file_id": null,
      "gemini_file_uri": null,
      "status": "uploaded",
      "uploaded_at": "2026-01-12T..."
    }
  ]
}
```

### Step 2: Sync PDF to Gemini
```bash
curl -X POST http://localhost:8000/api/pdfs/sync \
  -H "Content-Type: application/json" \
  -d "{\"filename\": \"your-research-paper.pdf\", \"category\": \"research_papers\"}"
```

**Expected Response:**
```json
{
  "message": "PDF synced successfully",
  "gemini_file_id": "files/abc123...",
  "status": "processing"
}
```

### Step 3: Check Processing Status
Wait 10-30 seconds, then check status:
```bash
curl http://localhost:8000/api/pdfs
```

Look for `"status": "active"` in the response.

### Step 4: Query the Document
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"What is this research paper about?\",
    \"session_id\": \"test-session-123\"
  }"
```

**Expected Response:**
```json
{
  "response": "This research paper discusses...",
  "sources": [
    {
      "filename": "your-research-paper.pdf",
      "category": "research_papers",
      "relevance": "high"
    }
  ],
  "session_id": "test-session-123"
}
```

---

## Option 3: Test via Python Console

### Quick Interactive Test
```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. List PDFs
response = requests.get(f"{BASE_URL}/pdfs")
print("PDFs:", response.json())

# 2. Sync a PDF (replace with your filename)
sync_data = {
    "filename": "your-research-paper.pdf",
    "category": "research_papers"
}
response = requests.post(f"{BASE_URL}/pdfs/sync", json=sync_data)
print("Sync result:", response.json())

# 3. Wait a bit for processing
import time
time.sleep(15)

# 4. Query the document
query_data = {
    "message": "What is this research paper about?",
    "session_id": "test-session-123"
}
response = requests.post(f"{BASE_URL}/chat/message", json=query_data)
result = response.json()
print("\nResponse:", result["response"])
print("\nSources:", result["sources"])
```

---

## Verification Checklist

### ✅ PDF Upload Verification
- [ ] PDF file exists in `backend/data/documents/research_papers/`
- [ ] PDF appears in the list when calling `/api/pdfs`
- [ ] File size is reasonable (not corrupted)

### ✅ Gemini Sync Verification
- [ ] Sync request returns success with `gemini_file_id`
- [ ] Status changes from "uploaded" → "processing" → "active"
- [ ] No error messages in backend logs

### ✅ Query Response Verification
- [ ] Response is relevant to the query
- [ ] Response includes content from the PDF
- [ ] Sources array includes the PDF filename
- [ ] Response time is reasonable (< 10 seconds)

### ✅ Citation Verification
- [ ] When asking for quotes, actual text from PDF is returned
- [ ] Source attribution is correct
- [ ] Multiple queries return consistent information

---

## Sample Queries for Research Papers

### Understanding the Paper
```
- "Summarize the main objectives of this research"
- "What problem is this paper trying to solve?"
- "Who are the authors and what institution are they from?"
```

### Methodology
```
- "What research methods were used in this study?"
- "Describe the experimental setup"
- "What data sources were used?"
```

### Results & Findings
```
- "What were the key findings?"
- "What conclusions did the authors reach?"
- "Were there any limitations mentioned?"
```

### Specific Details
```
- "What statistical methods were used?"
- "How many participants/samples were in the study?"
- "What are the implications of this research?"
```

---

## Troubleshooting

### Issue: PDF Not Appearing in List
**Solution:**
1. Check file is in correct directory: `backend/data/documents/research_papers/`
2. Restart the backend server
3. Check file permissions

### Issue: Sync Fails with Error
**Possible Causes:**
- Invalid Gemini API key → Check `backend/.env`
- PDF file corrupted → Try re-uploading
- File too large → Gemini has size limits (check docs)

**Check Backend Logs:**
Look in Terminal 4 for error messages

### Issue: Status Stuck on "Processing"
**Solution:**
1. Wait 30-60 seconds (large PDFs take time)
2. Check Gemini API quota/limits
3. Try syncing again

### Issue: Query Returns Generic Response
**Possible Causes:**
- PDF not fully processed yet
- Query too vague
- PDF content not relevant to query

**Solution:**
1. Verify status is "active"
2. Try more specific queries
3. Check if PDF content matches your query

### Issue: No Sources in Response
**Possible Causes:**
- RAG not finding relevant content
- PDF not properly indexed

**Solution:**
1. Re-sync the PDF
2. Try queries that directly relate to PDF content
3. Check backend logs for RAG service errors

---

## Expected Processing Times

| Action | Expected Time |
|--------|---------------|
| PDF Upload | Instant |
| Sync to Gemini | 2-5 seconds |
| Gemini Processing | 10-60 seconds (depends on PDF size) |
| Query Response | 3-8 seconds |

---

## Backend Log Monitoring

Watch Terminal 4 for these log messages:

**Successful Sync:**
```
INFO: PDF synced to Gemini: your-research-paper.pdf
INFO: Gemini file ID: files/abc123...
```

**Processing Complete:**
```
INFO: PDF processing complete: your-research-paper.pdf
INFO: Status: active
```

**Query Processing:**
```
INFO: Processing chat message with RAG
INFO: Found 1 relevant documents
INFO: Generated response with sources
```

---

## Quick Test Workflow

**5-Minute Test:**
1. ✅ Verify PDF in directory (30 sec)
2. ✅ Call `/api/pdfs` to list (10 sec)
3. ✅ Sync PDF via API or UI (30 sec)
4. ✅ Wait for processing (30 sec)
5. ✅ Send test query (10 sec)
6. ✅ Verify response has sources (10 sec)
7. ✅ Try 2-3 more queries (2 min)

**Total: ~5 minutes**

---

## Success Criteria

Your PDF RAG implementation is working correctly if:

✅ PDF syncs to Gemini without errors
✅ Status reaches "active" state
✅ Queries return relevant responses
✅ Responses include source citations
✅ Multiple queries work consistently
✅ Response quality is good (not generic)

---

## Next Steps After Testing

Once basic testing is complete:

1. **Test with Multiple PDFs** - Upload and sync 2-3 different papers
2. **Test Cross-Document Queries** - Ask questions that span multiple papers
3. **Test Edge Cases** - Very long queries, technical jargon, etc.
4. **Performance Testing** - Multiple rapid queries
5. **UI/UX Testing** - Test the complete user flow in the frontend

---

## Need Help?

- Check backend logs in Terminal 4
- Review `PDF_RAG_IMPLEMENTATION_PLAN.md` for architecture details
- Check Gemini API documentation for file API limits
- Verify `.env` configuration is correct

---

**Happy Testing! 🚀**