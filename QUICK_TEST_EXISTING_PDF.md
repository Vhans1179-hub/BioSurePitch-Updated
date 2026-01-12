# Quick Test with Existing PDF

Your PDF file `surgical-staplers-and-staples-labeling-guidance.pdf` is already uploaded!

## Step 1: Sync the PDF to Gemini

In your browser at http://localhost:5137, click the **"Sync to Gemini"** button in the PDF Manager.

This will upload the PDF to Gemini's File API for processing.

**Wait 10-30 seconds** for Gemini to process the file. The status badge will change from "Not Synced" → "Processing" → "Active"

## Step 2: Query the Document

Once the status shows **"Active"**, you can ask questions in the chat. Try these queries:

### Sample Queries:

**General Understanding:**
```
What is this document about?
```

**Specific Information:**
```
What are the key recommendations for surgical stapler labeling?
```

**Detailed Questions:**
```
What safety considerations are mentioned for surgical staplers?
```

**Citation Test:**
```
Can you quote the main purpose of this guidance document?
```

## Expected Results:

✅ The chat will respond with relevant information from the PDF
✅ You'll see source citations showing the PDF was used
✅ Responses will be specific to the document content

## Troubleshooting:

**If sync fails with authentication error:**
- Check that your `GEMINI_API_KEY` is set in `backend/.env`
- The error in the logs shows an OAuth issue - you may need to use the Gemini API key correctly

**If status stays on "Processing":**
- Wait up to 60 seconds for large PDFs
- Refresh the page to check updated status

**If queries don't use the PDF:**
- Verify the status is "Active" (green badge with checkmark)
- Try more specific questions related to surgical staplers

---

## Alternative: Test via API

If you prefer to test via command line:

### 1. Sync the PDF:
```bash
curl -X POST "http://localhost:8000/api/v1/pdfs/sync?category=research_papers"
```

### 2. Wait 15 seconds, then query:
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is this document about surgical staplers?\", \"session_id\": \"test-123\"}"
```

The response will include the answer and source citations.