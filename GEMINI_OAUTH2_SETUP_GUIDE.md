# Gemini File API OAuth2 Setup Guide

The Gemini File API requires OAuth2 authentication (service account credentials), not API keys. Follow these steps to set it up.

---

## Step 1: Create a Service Account

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/iam-admin/serviceaccounts
   - Select your project

2. **Create Service Account**
   - Click "Create Service Account"
   - **Service account name**: `gemini-file-api-service`
   - **Service account ID**: Will auto-generate (e.g., `gemini-file-api-service@your-project.iam.gserviceaccount.com`)
   - **Description**: "Service account for Gemini File API access"
   - Click "Create and Continue"

3. **Grant Permissions** (Step 2 of wizard)
   - Click "Select a role"
   - Search for and select: **"Generative Language API User"**
   - If that role doesn't exist, use: **"Editor"** (less secure but will work)
   - Click "Continue"

4. **Skip Step 3** (Grant users access)
   - Click "Done"

---

## Step 2: Create and Download Service Account Key

1. **Find Your Service Account**
   - In the service accounts list, find `gemini-file-api-service`
   - Click on the email address

2. **Create Key**
   - Go to the "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select **JSON** format
   - Click "Create"
   - A JSON file will download automatically (e.g., `your-project-abc123.json`)

3. **Save the Key File**
   - Move the downloaded JSON file to your project:
     ```
     backend/credentials/gemini-service-account.json
     ```
   - Create the `credentials` directory if it doesn't exist

---

## Step 3: Enable Required APIs

1. **Enable Generative Language API**
   - Visit: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
   - Select your project
   - Click "Enable"

2. **Verify API is Enabled**
   - Go to: https://console.cloud.google.com/apis/dashboard
   - You should see "Generative Language API" in the list

---

## Step 4: Update Backend Configuration

### 4.1 Create Credentials Directory
```bash
mkdir backend/credentials
```

### 4.2 Move Service Account Key
Move your downloaded JSON file to:
```
backend/credentials/gemini-service-account.json
```

### 4.3 Update .gitignore
Add to `.gitignore` to prevent committing credentials:
```
backend/credentials/
*.json
!package.json
!tsconfig*.json
```

### 4.4 Update backend/.env
Add this line to `backend/.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=backend/credentials/gemini-service-account.json
```

Keep your existing `GEMINI_API_KEY` for the generation API (chat).

---

## Step 5: Install Required Python Package

The service account authentication requires the `google-auth` package:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

Or add to `backend/requirements.txt`:
```
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
```

Then run:
```bash
pip install -r backend/requirements.txt
```

---

## Step 6: Update Gemini RAG Service

The code needs to be modified to use service account credentials instead of API keys for File API operations.

I'll update the `backend/services/gemini_rag_service.py` file to support both:
- **API Key**: For generation/chat (works as-is)
- **Service Account**: For File API operations (upload, list, delete)

---

## Step 7: Test the Setup

After completing the above steps:

1. **Restart the Backend**
   - The backend should auto-reload when you save the updated files
   - Or manually restart: `Ctrl+C` in Terminal 4, then run `python -m uvicorn backend.main:app --reload`

2. **Test PDF Sync**
   - Go to http://localhost:5137
   - Click "Sync to Gemini"
   - Should succeed this time!

3. **Verify in Logs**
   - Check Terminal 4 for success messages
   - Should see: "PDF synced successfully" instead of authentication errors

---

## Troubleshooting

### Error: "Could not load credentials"
- Verify the JSON file path is correct
- Check file permissions (should be readable)
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` path is correct in `.env`

### Error: "Permission denied"
- Verify the service account has "Generative Language API User" role
- Check that the API is enabled in your project

### Error: "API not enabled"
- Go to https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
- Click "Enable"

---

## Security Best Practices

1. **Never commit credentials to Git**
   - Always add `backend/credentials/` to `.gitignore`
   - Use environment variables for production

2. **Rotate Keys Regularly**
   - Delete old service account keys
   - Create new ones periodically

3. **Use Least Privilege**
   - Only grant necessary permissions
   - Use "Generative Language API User" role, not "Editor"

4. **For Production**
   - Use Google Cloud Secret Manager
   - Set up Workload Identity if deploying to GKE
   - Use environment-specific service accounts

---

## Next Steps

Once you complete Steps 1-4 above, let me know and I'll:
1. Update the `gemini_rag_service.py` to use service account authentication
2. Test the PDF sync functionality
3. Verify everything works end-to-end

---

## Quick Checklist

- [ ] Created service account in Google Cloud Console
- [ ] Downloaded JSON key file
- [ ] Moved key file to `backend/credentials/gemini-service-account.json`
- [ ] Enabled Generative Language API
- [ ] Updated `.gitignore` to exclude credentials
- [ ] Added `GOOGLE_APPLICATION_CREDENTIALS` to `backend/.env`
- [ ] Installed `google-auth` packages
- [ ] Ready for code updates

Let me know when you've completed these steps!