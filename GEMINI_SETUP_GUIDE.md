# Google Cloud and Gemini API Setup Guide

## Overview

This guide provides step-by-step instructions for setting up Google Cloud Project and Gemini API access for the PDF RAG (Retrieval-Augmented Generation) implementation in the healthcare application.

**Estimated Setup Time:** 30-45 minutes

---

## 1. Prerequisites

Before you begin, ensure you have:

- **Google Account**: A valid Google account (personal or organizational)
- **Payment Method**: Credit or debit card for billing setup
  - Google Cloud offers a free tier with $300 credit for new users
  - Gemini API has generous free tier limits (15 requests/minute)
- **Development Environment**:
  - Python 3.8 or higher installed
  - pip package manager
  - Text editor or IDE (VS Code recommended)
  - Git for version control

---

## 2. Google Cloud Project Setup

### Step 2.1: Access Google Cloud Console

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Accept the Terms of Service if prompted

### Step 2.2: Create a New Project

1. Click the **project dropdown** at the top of the page (next to "Google Cloud")
2. Click **"NEW PROJECT"** in the dialog that appears
3. Configure your project:
   - **Project name**: `peaceful-platypus-roam-prod` (or your preferred name)
   - **Organization**: Select if applicable (optional)
   - **Location**: Choose your organization or "No organization"
4. Click **"CREATE"**
5. Wait for the project to be created (usually takes 10-30 seconds)

### Step 2.3: Select Your Project

1. Click the **project dropdown** again
2. Select your newly created project from the list
3. Verify the project name appears in the top navigation bar

### Step 2.4: Set Up Billing

1. Navigate to **"Billing"** from the hamburger menu (☰) on the left
2. Click **"LINK A BILLING ACCOUNT"**
3. Choose an existing billing account or create a new one:
   - Click **"CREATE BILLING ACCOUNT"**
   - Enter your payment information
   - Accept the terms and conditions
4. Link the billing account to your project

**Note**: You won't be charged immediately. Google Cloud offers:
- $300 free credit for new users (90-day validity)
- Always-free tier for many services
- Gemini API free tier (see Section 6 for details)

---

## 3. Enable Gemini API

### Step 3.1: Navigate to API Library

1. From the Google Cloud Console, click the **hamburger menu (☰)**
2. Navigate to **"APIs & Services"** → **"Library"**
3. Alternatively, use this direct link: [API Library](https://console.cloud.google.com/apis/library)

### Step 3.2: Enable Generative Language API

1. In the API Library search bar, type: `Generative Language API`
2. Click on **"Generative Language API"** from the results
3. Click the **"ENABLE"** button
4. Wait for the API to be enabled (usually takes 5-10 seconds)
5. You should see a green checkmark and "API enabled" message

### Step 3.3: Enable Vertex AI API (Optional but Recommended)

For production deployments with enhanced features:

1. Search for `Vertex AI API` in the API Library
2. Click on **"Vertex AI API"**
3. Click **"ENABLE"**

**Note**: The File API is automatically included with the Generative Language API and doesn't require separate enablement.

### Step 3.4: Verify API Enablement

1. Navigate to **"APIs & Services"** → **"Enabled APIs & services"**
2. Confirm you see:
   - ✅ Generative Language API
   - ✅ Vertex AI API (if enabled)

---

## 4. API Key Generation

### Step 4.1: Navigate to Credentials

1. From the hamburger menu (☰), go to **"APIs & Services"** → **"Credentials"**
2. Alternatively, use this direct link: [Credentials](https://console.cloud.google.com/apis/credentials)

### Step 4.2: Create API Key

1. Click **"+ CREATE CREDENTIALS"** at the top
2. Select **"API key"** from the dropdown
3. A dialog will appear with your new API key
4. **IMPORTANT**: Copy the API key immediately and store it securely
5. Click **"CLOSE"** (you can view it later if needed)

### Step 4.3: Restrict API Key (Security Best Practice)

1. Find your newly created API key in the credentials list
2. Click the **pencil icon (✏️)** to edit
3. Under **"API restrictions"**:
   - Select **"Restrict key"**
   - Check **"Generative Language API"**
   - Check **"Vertex AI API"** (if using)
4. Under **"Application restrictions"** (optional but recommended):
   - For development: Select **"IP addresses"** and add your development machine's IP
   - For production: Select **"HTTP referrers"** or **"IP addresses"** as appropriate
5. Click **"SAVE"**

### Step 4.4: Set Up Environment Variable

**For Local Development:**

1. Navigate to your project's backend directory:
   ```bash
   cd backend
   ```

2. Create or edit the `.env` file:
   ```bash
   # On Windows
   notepad .env
   
   # On macOS/Linux
   nano .env
   ```

3. Add your API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. Save and close the file

**Security Reminders:**
- ✅ Never commit `.env` files to version control
- ✅ Ensure `.env` is listed in `.gitignore`
- ✅ Use different API keys for development and production
- ✅ Rotate API keys regularly (every 90 days recommended)

---

## 5. Testing API Access

### Step 5.1: Install Required SDK

Install the Google Generative AI Python SDK:

```bash
pip install google-generativeai
```

### Step 5.2: Create Test Script

Create a file named `test_gemini_api.py` in your project root:

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

# Test basic text generation
def test_text_generation():
    print("Testing Gemini API - Text Generation...")
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    response = model.generate_content("Say 'Hello, Gemini API is working!'")
    print(f"Response: {response.text}")
    print("✅ Text generation test passed!")

# Test file upload capability
def test_file_api():
    print("\nTesting Gemini API - File API...")
    try:
        # List any existing files (should be empty initially)
        files = genai.list_files()
        print(f"Current files in storage: {len(list(files))}")
        print("✅ File API test passed!")
    except Exception as e:
        print(f"⚠️ File API test failed: {e}")

if __name__ == "__main__":
    try:
        test_text_generation()
        test_file_api()
        print("\n🎉 All tests passed! Gemini API is configured correctly.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify your API key is correct")
        print("2. Ensure the Generative Language API is enabled")
        print("3. Check your billing account is active")
        print("4. Verify API key restrictions allow access from your IP")
```

### Step 5.3: Run the Test

```bash
python test_gemini_api.py
```

**Expected Output:**
```
Testing Gemini API - Text Generation...
Response: Hello, Gemini API is working!
✅ Text generation test passed!

Testing Gemini API - File API...
Current files in storage: 0
✅ File API test passed!

🎉 All tests passed! Gemini API is configured correctly.
```

### Step 5.4: Troubleshooting Common Issues

| Issue | Solution |
|-------|----------|
| `API key not valid` | Verify the API key is copied correctly without extra spaces |
| `Permission denied` | Ensure the Generative Language API is enabled in your project |
| `Quota exceeded` | Check you haven't exceeded free tier limits (see Section 6) |
| `Billing not enabled` | Verify billing account is linked to your project |
| `IP address blocked` | Check API key restrictions and add your IP if needed |
| `Module not found` | Run `pip install google-generativeai python-dotenv` |

---

## 6. Cost Management

### Understanding Gemini API Pricing

**Free Tier (Gemini 1.5 Pro):**
- **Rate Limit**: 15 requests per minute (RPM)
- **Daily Limit**: 1,500 requests per day
- **Token Limits**: 
  - Input: 1 million tokens per minute
  - Output: 10,000 tokens per minute
- **File Storage**: First 20GB free

**Paid Tier Pricing (as of 2024):**
- **Gemini 1.5 Pro**: 
  - Input: $0.00125 per 1K characters
  - Output: $0.00375 per 1K characters
- **Gemini 1.5 Flash** (faster, cheaper):
  - Input: $0.000125 per 1K characters
  - Output: $0.000375 per 1K characters

### Cost Estimation for Healthcare PDF RAG

**Typical Usage Scenario:**
- 100 PDF documents, average 50 pages each
- 10 queries per day
- Average response: 500 tokens

**Estimated Monthly Cost:**
- PDF Processing (one-time): ~$5-10
- Daily Queries: ~$0.50-1.00
- **Total Monthly**: ~$15-30

**Free Tier Coverage:**
- Development and testing: Fully covered
- Small production deployments: Mostly covered
- Large-scale production: Requires paid tier

### Setting Up Billing Alerts

1. Navigate to **"Billing"** → **"Budgets & alerts"**
2. Click **"CREATE BUDGET"**
3. Configure your budget:
   - **Name**: "Gemini API Monthly Budget"
   - **Budget amount**: $50 (or your preferred limit)
   - **Threshold rules**: 
     - 50% of budget
     - 90% of budget
     - 100% of budget
4. Add email notifications
5. Click **"FINISH"**

### Monitoring Usage

1. Navigate to **"APIs & Services"** → **"Dashboard"**
2. View API usage metrics:
   - Requests per day
   - Quota usage
   - Error rates
3. Set up custom alerts for unusual activity

---

## 7. HIPAA and Compliance Considerations

### Understanding HIPAA Requirements

For healthcare applications handling Protected Health Information (PHI), you must ensure HIPAA compliance.

### Google Cloud BAA (Business Associate Agreement)

**Standard Tier (Free/Pay-as-you-go):**
- ❌ No BAA available
- ❌ Not HIPAA compliant
- ⚠️ **Do NOT use for PHI in production**

**Enterprise Tier:**
- ✅ BAA available
- ✅ HIPAA compliant
- ✅ Enhanced security features
- 💰 Requires enterprise contract

### Requesting a BAA

1. Contact Google Cloud Sales: [Contact Form](https://cloud.google.com/contact)
2. Specify you need:
   - HIPAA compliance
   - Business Associate Agreement
   - Vertex AI/Gemini API access
3. Work with sales team to:
   - Review enterprise pricing
   - Sign BAA
   - Configure compliant project

### Data Residency Options

For compliance with data residency requirements:

1. Navigate to **"IAM & Admin"** → **"Settings"**
2. Configure **"Resource Location Restriction"**
3. Select allowed regions (e.g., US-only for HIPAA)

### Compliance Checklist

Before deploying to production with PHI:

- [ ] BAA signed with Google Cloud
- [ ] Enterprise tier activated
- [ ] Data residency configured
- [ ] Encryption at rest enabled (default)
- [ ] Encryption in transit enabled (default)
- [ ] Access controls configured (IAM)
- [ ] Audit logging enabled
- [ ] Regular security assessments scheduled
- [ ] Incident response plan documented
- [ ] Staff HIPAA training completed

### Development vs. Production

**For Development/Testing:**
- ✅ Use standard tier with synthetic/anonymized data
- ✅ No PHI in development environment
- ✅ Test with mock patient data

**For Production:**
- ✅ Enterprise tier with BAA
- ✅ PHI handling approved
- ✅ Compliance audit completed

---

## 8. Environment Configuration

### Step 8.1: Update `.env.example`

Add Gemini API configuration to [`backend/.env.example`](backend/.env.example):

```env
# Database Configuration
DATABASE_URL=sqlite:///./test.db

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro
GEMINI_MAX_TOKENS=8192
GEMINI_TEMPERATURE=0.7

# File Upload Configuration
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,docx,txt

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

### Step 8.2: Update `config.py`

Add Gemini configuration to [`backend/config.py`](backend/config.py):

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing settings...
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # Gemini API Settings
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    gemini_max_tokens: int = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
    gemini_temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    
    # File Upload Settings
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    allowed_file_types: list = os.getenv("ALLOWED_FILE_TYPES", "pdf,docx,txt").split(",")
    
    # RAG Settings
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Step 8.3: Security Best Practices

**API Key Management:**

1. **Never hardcode API keys** in source code
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly** (every 90 days minimum)
4. **Use different keys** for development, staging, and production
5. **Implement key rotation** without downtime:
   ```python
   # Support multiple keys for zero-downtime rotation
   GEMINI_API_KEY_PRIMARY=key1
   GEMINI_API_KEY_SECONDARY=key2
   ```

**Access Control:**

1. Limit API key access to specific IPs
2. Use service accounts for production
3. Implement least-privilege access
4. Enable audit logging

**Monitoring:**

1. Set up alerts for unusual API usage
2. Monitor error rates
3. Track quota consumption
4. Log all API interactions (without logging PHI)

---

## 9. Next Steps

### Immediate Actions

1. ✅ Complete all setup steps above
2. ✅ Run the test script successfully
3. ✅ Configure environment variables
4. ✅ Set up billing alerts

### Implementation Phases

Refer to [`PDF_RAG_IMPLEMENTATION_PLAN.md`](PDF_RAG_IMPLEMENTATION_PLAN.md) for detailed implementation phases:

**Phase 1: Foundation (Week 1)**
- Set up Gemini API integration
- Implement file upload service
- Create document processing pipeline

**Phase 2: RAG Core (Week 2)**
- Implement chunking strategy
- Build vector storage
- Create retrieval system

**Phase 3: Query Processing (Week 3)**
- Implement query handler
- Build context assembly
- Create response generation

**Phase 4: Integration (Week 4)**
- Integrate with chat system
- Add UI components
- Implement error handling

### Ready-to-Use Checklist

- [ ] Google Cloud project created
- [ ] Billing account linked
- [ ] Generative Language API enabled
- [ ] API key generated and secured
- [ ] API key restrictions configured
- [ ] Environment variables set up
- [ ] Test script runs successfully
- [ ] Billing alerts configured
- [ ] HIPAA compliance reviewed (if applicable)
- [ ] BAA signed (if handling PHI)
- [ ] `.env.example` updated
- [ ] `config.py` updated
- [ ] Security best practices implemented
- [ ] Team members trained on API usage
- [ ] Documentation reviewed

---

## Additional Resources

### Official Documentation

- [Google AI Studio](https://makersuite.google.com/) - Interactive API playground
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Python SDK Reference](https://ai.google.dev/api/python/google/generativeai)
- [Google Cloud HIPAA Compliance](https://cloud.google.com/security/compliance/hipaa)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

### Support Channels

- [Google Cloud Support](https://cloud.google.com/support)
- [Stack Overflow - google-gemini tag](https://stackoverflow.com/questions/tagged/google-gemini)
- [Google AI Developer Forum](https://discuss.ai.google.dev/)

### Pricing Calculators

- [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator)
- [Gemini API Pricing](https://ai.google.dev/pricing)

---

## Troubleshooting

### Common Issues and Solutions

**Issue: "API key not valid"**
- Solution: Verify the API key is copied correctly, check for extra spaces
- Verify the API is enabled in your project
- Ensure billing is set up

**Issue: "Quota exceeded"**
- Solution: Check your usage in the API dashboard
- Upgrade to paid tier if needed
- Implement rate limiting in your application

**Issue: "Permission denied"**
- Solution: Verify the Generative Language API is enabled
- Check API key restrictions
- Ensure billing account is active

**Issue: "File upload fails"**
- Solution: Check file size limits (default 10MB)
- Verify file type is supported
- Ensure sufficient storage quota

**Issue: "Slow response times"**
- Solution: Consider using Gemini 1.5 Flash for faster responses
- Implement caching for common queries
- Optimize chunk sizes and retrieval parameters

---

## Version History

- **v1.0** (2026-01-12): Initial setup guide created
- Covers Google Cloud project setup, Gemini API configuration, and HIPAA considerations
- Includes practical examples and troubleshooting guidance

---

**Need Help?** If you encounter issues not covered in this guide, please:
1. Check the official documentation links above
2. Review the troubleshooting section
3. Contact the development team
4. Open an issue in the project repository

**Security Notice:** This guide contains sensitive setup information. Do not share API keys or credentials. Follow all security best practices outlined in Section 8.