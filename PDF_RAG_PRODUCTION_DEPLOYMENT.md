# PDF RAG Production Deployment Guide

This document outlines the network, infrastructure, and security requirements for deploying the PDF RAG (Retrieval-Augmented Generation) feature in a production environment, specifically tailored for healthcare client sites with strict compliance needs.

## 1. Network Connections & External Dependencies

The application requires the following outbound network connections. All traffic is encrypted via TLS 1.2+.

### Google Cloud APIs (Required for RAG)
| Service | Endpoint | Port | Protocol | Purpose |
|---------|----------|------|----------|---------|
| Gemini API | `generativelanguage.googleapis.com` | 443 | HTTPS | Main interface for chat and embeddings |
| File API | `generativelanguage.googleapis.com` | 443 | HTTPS | Uploading and managing PDF documents |
| OAuth2 (Optional) | `accounts.google.com` | 443 | HTTPS | If using Service Account authentication |

### Database Connectivity
| Service | Endpoint | Port | Protocol | Purpose |
|---------|----------|------|----------|---------|
| MongoDB | `*.<cluster-id>.mongodb.net` (Atlas) <br> OR `internal-ip` (On-prem) | 27017 | TCP | Storing chat history, user sessions, and metadata |

### Application Communication
| Direction | Source | Destination | Port | Protocol | Purpose |
|-----------|--------|-------------|------|----------|---------|
| Inbound | Client Workstations | Application Server | 80/443 | HTTP/S | Web interface access |
| Internal | Frontend | Backend API | 8000 | HTTP | Internal API calls (can be proxied via 443) |

## 2. Firewall & Network Configuration

### Outbound Rules (Egress)
Ensure the application server allows outbound traffic to:
*   **Destination:** `*.googleapis.com`
*   **Port:** `443`
*   **Protocol:** `TCP`

*Note: IP whitelisting for Google APIs is generally discouraged due to dynamic IP ranges. Use domain whitelisting if possible.*

### Corporate Proxy Configuration
If the client site uses an outbound proxy:
1.  **Environment Variables:** The Python backend respects standard proxy variables:
    ```bash
    export HTTP_PROXY="http://proxy.example.com:8080"
    export HTTPS_PROXY="http://proxy.example.com:8080"
    ```
2.  **SSL Inspection:** If the proxy performs SSL inspection, the corporate CA certificate must be added to the container/server's trusted certificate store or the Python `certifi` store.

### VPN Requirements
*   **Remote Access:** If IT support requires remote access for troubleshooting, a VPN with access to the application server on port 22 (SSH) and 8000 (API monitoring) is recommended.

## 3. Infrastructure Requirements

### Server Specifications (Minimum Recommendations)
*   **CPU:** 2 vCPUs (4 recommended for concurrent PDF processing)
*   **RAM:** 8 GB (16 GB recommended to handle large PDF in-memory processing)
*   **Storage:** 
    *   **OS/App:** 20 GB SSD
    *   **PDF Storage:** 100 GB+ SSD (Scalable based on document retention policy)
*   **OS:** Linux (Ubuntu 22.04 LTS / RHEL 8+) or Windows Server 2019+
*   **Runtime:** 
    *   Python 3.10+
    *   Node.js 18+ (for Frontend build)

### Database Requirements (MongoDB)
*   **Version:** MongoDB 5.0+
*   **Configuration:** Replica Set (Recommended for High Availability)
*   **Storage:** 50 GB+ for metadata and chat logs
*   **Backup:** Daily incremental backups required

### Storage Strategy
The application stores PDFs locally before uploading to Gemini.
*   **Path:** Configurable via `PDF_STORAGE_PATH` (Default: `backend/data/documents`)
*   **Security:** This directory must be encrypted at the filesystem level (e.g., LUKS, BitLocker).

## 4. Security & Compliance (HIPAA)

### Google Cloud BAA
**CRITICAL:** For HIPAA compliance, a Business Associate Agreement (BAA) MUST be signed with Google Cloud. The Gemini API is HIPAA-compliant **only** when used under a BAA-covered project.
*   Ensure the GCP Project used has the proper "Healthcare" settings enabled where applicable.

### Data Encryption
*   **In Transit:** All traffic MUST use TLS 1.2 or higher.
    *   Enable HTTPS on the application server using Nginx/Apache as a reverse proxy.
    *   Ensure MongoDB connection string includes `tls=true`.
*   **At Rest:**
    *   Enable Disk Encryption on the server.
    *   Enable Encryption at Rest for the MongoDB database.

### Access Control
*   **API Keys:** `GEMINI_API_KEY` provides access to the AI model.
    *   **Do not** commit this key to code.
    *   Use a Secrets Manager (AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault) to inject this into the runtime environment.
    *   Rotate keys every 90 days.

### Audit Logging
*   The application logs interactions. Ensure these logs are shipped to a centralized SIEM (e.g., Splunk, Datadog) for audit trails.
*   **Log Retention:** Minimum 6 years (standard HIPAA requirement, verify with client compliance officer).

## 5. Environment Configuration

Create a `.env.production` file on the deployment server.

```ini
# Application Settings
APP_NAME="BioSure Production"
APP_ENV="production"
DEBUG=False

# API Configuration
HOST="0.0.0.0"
PORT=8000
# Comma-separated list of allowed origins (e.g., the frontend domain)
CORS_ORIGINS="https://biosure.internal.hospital.org"

# Security
SECRET_KEY="<GENERATED_STRONG_RANDOM_STRING>"

# Database
# Use a service account with restricted permissions
MONGODB_URI="mongodb+srv://app_user:<password>@cluster.mongodb.net/biosure_db?retryWrites=true&w=majority&tls=true"
DATABASE_NAME="biosure_prod"

# Gemini AI Service
GEMINI_API_KEY="<YOUR_PROD_API_KEY>"
GEMINI_MODEL="gemini-1.5-pro-latest"

# Storage
# Ensure this path allows read/write for the app user
PDF_STORAGE_PATH="/opt/biosure/data/documents"
```

## 6. Deployment Architecture Options

### Option 1: On-Premise (Docker Compose) - Recommended for High Security
*   **Pros:** Data stays within client perimeter until sent to Gemini API; easiest for legacy IT integration.
*   **Cons:** Requires manual updates; client manages hardware.
*   **Network:** Only outbound 443 to Google required.

### Option 2: Private Cloud (AWS/Azure VPC)
*   **Pros:** Scalable; managed infrastructure; easier backups.
*   **Cons:** Requires VPN/Direct Connect for internal hospital network access.
*   **Network:** Site-to-Site VPN or PrivateLink.

## 7. Client Site Checklist (Pre-Deployment)

Provide this list to the client's Network/IT team 1 week prior to deployment.

- [ ] **Firewall:** Whitelisted `*.googleapis.com` on port 443 (Outbound).
- [ ] **DNS:** Internal DNS record created for application (e.g., `ai-search.hospital.local`).
- [ ] **SSL:** Wildcard or specific SSL certificate provided for the internal domain.
- [ ] **Service Account:** Dedicated Service Account created for the application on the VM/Container.
- [ ] **Storage:** Persistent volume provisioned for PDF storage (min 100GB).
- [ ] **Proxy:** Proxy details (URL, Port, Auth) provided if applicable.

## 8. Troubleshooting Network Issues

**1. Test Google API Connectivity:**
From the application server:
```bash
curl -v https://generativelanguage.googleapis.com
```
*Expected: SSL handshake success, HTTP 404 (normal for root path) or 200.*

**2. Test MongoDB Connectivity:**
```bash
# If using local tools
mongosh "mongodb+srv://<host>" --username <user>
# Or verify via telnet/nc
nc -zv <mongo-host> 27017
```

**3. Verify DNS Resolution:**
```bash
nslookup generativelanguage.googleapis.com
```

**Common Errors:**
*   `SSL verification failed`: Check corporate proxy certificate injection.
*   `Connection timed out`: Firewall blocking port 443 outbound.

## 9. Monitoring & Maintenance

*   **Health Check Endpoint:** `GET /health` (Configure Load Balancer to poll this).
*   **Logs:** Monitor for `ERROR` level logs in `/var/log/biosure/app.log`.
*   **Backups:** Schedule a cron job to backup the `PDF_STORAGE_PATH` and `mongodump` nightly.

## 10. Client Communication Template

**Subject:** Network Requirements for BioSure AI Deployment

**Body:**

Dear IT Team,

To proceed with the deployment of the BioSure RAG module, we require the following network configurations to be verified:

**1. Outbound Access:**
The application server (IP: `<Target_Server_IP>`) needs HTTPS (TCP/443) access to:
*   `generativelanguage.googleapis.com` (Google Gemini API)

**2. Internal Access:**
*   Users need HTTP/HTTPS access to the application server on port 80/443.

**3. Service Account:**
Please provide a service account with read/write access to the designated storage directory `/opt/biosure/data`.

**Network Diagram:**

```
[User Workstation]  <---(HTTPS/443)--->  [BioSure App Server]  <---(HTTPS/443)--->  [Google Gemini API]
       |                                          |
       |                                          |
       +------------------------------------------+
                      (Private Network)
```

Please let us know if you have any questions regarding these requirements.

Best regards,
Deployment Team