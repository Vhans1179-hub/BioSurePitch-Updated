# PDF RAG Implementation Plan & Architecture

## 1. Approach Overview & Migration Strategy

### Strategy: "Gemini First" with Hybrid Evolution
We will implement **Option 1 (Gemini File API)** as the initial solution. This leverages Google's managed infrastructure for document processing, caching, and retrieval (Long Context Window), allowing for rapid development and superior accuracy without managing a local vector database immediately.

**Why this approach?**
- **Speed to Value:** No need to setup embeddings, vector stores (Chroma/FAISS), or chunking strategies.
- **Accuracy:** Gemini 1.5 Pro's long context window (up to 2M tokens) often outperforms retrieval-based RAG for complex reasoning across full documents.
- **Simplicity:** Reduces infrastructure complexity in the early stage.

### Architecture Principles for Future Hybrid Migration
To ensure we can migrate to a Hybrid approach (keeping sensitive PHI local) in the future without a rewrite, we will adhere to these principles:

1.  **Service Abstraction:** We will create a generic `RAGService` interface. The rest of the application (Chat Engine) will talk to this interface, not directly to Gemini or a Vector DB.
2.  **Document Metadata:** All documents will be tagged with a `classification` level (e.g., `PUBLIC`, `INTERNAL`, `PHI`).
3.  **Abstracted Querying:** The `query(message, context_docs)` function will be designed to accept "retrieved context" regardless of whether that context came from Gemini's cache or a local vector store.

---

## 2. Google Cloud/Gemini Setup Requirements

### 2.1 Project Setup
1.  **Create Google Cloud Project:** Create a new project named `biosure-medai-platform`.
2.  **Enable APIs:**
    -   **Generative Language API:** For Gemini 1.5 Pro access.
    -   **Google Cloud Storage API:** (Optional, if we move to GCS buckets later, but File API handles uploads directly for now).
3.  **API Keys:**
    -   Generate an API Key in Google AI Studio.
    -   **Security:** Store this key in `.env` as `GOOGLE_API_KEY`. **NEVER** commit it to git.

### 2.2 Quota & Cost Management
-   **Model:** `gemini-1.5-pro-latest` (Recommended for complex PDF reasoning).
-   **Cost Control:**
    -   Gemini File API has storage costs per GB/month and inference costs per 1M tokens.
    -   **Optimization:** We will cache the uploaded files using Gemini's context caching if frequently accessed, or rely on ephemeral file uploads for session-based chats.
-   **BAA (HIPAA):**
    -   *Critical:* For a HIPAA-compliant production environment, we must ensure the Google Cloud project is covered by a BAA.
    -   *Note:* The free tier of Gemini API is **NOT** HIPAA compliant. Enterprise/Paid tier usage must be configured for compliance.

---

## 3. Backend Architecture

### 3.1 Document Storage Structure
We will organize source PDFs locally in the repo (as requested):

```text
backend/
  data/
    documents/
      research_papers/    # Medical journals, clinical studies
      clinical_guidelines/ # Standard operating procedures
      policies/           # Healthcare policies, insurance docs
      patient_records/    # (Future/Test) Anonymized records
```

### 3.2 Service Layer Design
We will introduce a new `RAGService` that implements the "Gemini First" logic but is ready for Hybrid.

**Interface:**
```python
class BaseRAGService(ABC):
    async def upload_document(file_path: str, category: str)
    async def list_documents()
    async def query(user_message: str, file_ids: List[str] = None)
```

**Implementation (`GeminiRAGService`):**
-   **File Manager:** Wraps `google.generativeai.files`. Handles uploading PDFs and waiting for processing state (`ACTIVE`).
-   **Chat Session:** Manages `model.start_chat` with `history` and loaded file resources.

### 3.3 Integration with `ChatEngine`
We will create a new specialized handler: `PDFKnowledgeHandler`.

-   **Trigger:** Explicit intent (e.g., "Check the guidelines for...") or fallback from `GeneralChatHandler` when medical context is detected.
-   **Flow:**
    1.  User asks question.
    2.  `ChatEngine` routes to `PDFKnowledgeHandler`.
    3.  Handler calls `RAGService.query(message)`.
    4.  `RAGService` constructs the prompt with the uploaded file handles.
    5.  Gemini returns answer + citations.

---

## 4. Technical Implementation Details

### 4.1 Dependencies
Update `backend/requirements.txt`:
```text
google-generativeai>=0.8.0  # Official SDK supporting File API
python-multipart            # For file upload endpoints
pypdf                       # For local validation/metadata extraction
```

### 4.2 Configuration (`.env`)
```ini
GOOGLE_API_KEY=AIzaSy...
GEMINI_MODEL_NAME=gemini-1.5-pro-latest
RAG_STORAGE_PATH=backend/data/documents
```

### 4.3 PDF Processing Workflow (Gemini File API)
1.  **Discovery:** On startup, `RAGService` scans `backend/data/documents`.
2.  **Sync:** Checks if files are already uploaded to Gemini (using `files.list`).
    -   *Optimization:* specific metadata (hash) to avoid re-uploading identical files.
3.  **Upload:**
    -   `genai.upload_file(path, mime_type="application/pdf")`
    -   Loop/Wait until `file.state.name == "ACTIVE"`.
4.  **Querying:**
    -   Construct request: `model.generate_content([user_prompt, file_ref])`

### 4.4 Error Handling
-   **File Too Large:** Catch 413 errors.
-   **Processing Failed:** Retry logic for files that get stuck in "PROCESSING".
-   **Rate Limits:** Implement exponential backoff for 429 errors.

---

## 5. Frontend Integration

### 5.1 Chat Interface Updates
-   **Source Citations:** Gemini responses often include citations. We need to parse these and display them in the UI.
    -   *Design:* "According to [Clinical Guidelines 2024], the treatment is..." -> Hovering shows the document name.
-   **Context Indicator:** A small badge showing which documents are currently "active" in the context window.

### 5.2 Document Management UI (Admin/Dev)
-   Simple view to see list of available PDFs.
-   Status indicator: "Syncing with AI...", "Ready".

---

## 6. Security and Compliance

### 6.1 Current HIPAA Considerations
-   **Gemini File API:** Data sent to the File API is stored by Google.
    -   *Constraint:* For this initial phase, **DO NOT** upload real PHI (Patient Health Information) to the standard API endpoint unless a BAA is in place and Enterprise endpoints are used.
    -   *Mitigation:* We will use **anonymized/synthetic** data for `patient_records` during development.

### 6.2 Data Privacy
-   **API Keys:** Strict environment variable usage.
-   **Audit Logging:** Log every query that accesses medical documents (User ID, Query, Document Accessed, Timestamp).

---

## 7. Migration Path to Hybrid (The "Future State")

When the need arises (e.g., strictly local PHI processing), we will migrate to **Hybrid RAG**:

1.  **Classification System:**
    -   Tag docs: `SENSITIVE` (Local) vs `GENERAL` (Cloud).
2.  **Local RAG Stack:**
    -   Install `chromadb` and `sentence-transformers` (or `FastEmbed`).
    -   Implement `LocalRAGService`.
3.  **Hybrid Logic:**
    ```python
    if doc.type == SENSITIVE:
        context = LocalVectorDB.search(query)
        prompt = f"Context: {context}\nQuestion: {query}"
        # Send text-only prompt to LLM (no file upload)
    else:
        # Use existing File API upload method
    ```

---

## 8. Testing Strategy

1.  **Unit Tests:**
    -   Test `PDFKnowledgeHandler` routing logic.
    -   Test PDF mime-type validation.
2.  **Integration Tests:**
    -   Mock `google.generativeai` to test the service flow without incurring costs.
    -   Real "Smoke Test": Script to upload one small PDF and ask a specific question to verify end-to-end connectivity.
3.  **Test Data:**
    -   Use public PubMed Central papers (Open Access) for testing research paper logic.
    -   Create synthetic patient PDFs for clinical record testing.

---

## 9. Implementation Phases

### Phase 1: Core Integration (backend)
-   [ ] Install `google-generativeai`.
-   [ ] Create `backend/services/rag_service.py` (Gemini implementation).
-   [ ] Implement PDF discovery and upload sync routine.
-   [ ] Create `PDFKnowledgeHandler` in `chat_handlers.py`.
-   [ ] Register handler in `ChatEngine`.

### Phase 2: Frontend & Refinement
-   [ ] Update Chat UI to render markdown citations nicely.
-   [ ] Add "Thinking..." state for longer PDF processing times.
-   [ ] Add "Sources" collapsible section to chat bubbles.

### Phase 3: Production Hardening
-   [ ] Implement proper file caching/hashing to prevent duplicate uploads.
-   [ ] Add comprehensive error handling for API timeouts.
-   [ ] Security review of API key handling.
