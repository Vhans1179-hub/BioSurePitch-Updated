# HCO Address Search - Current Status & Diagnosis

## Problem Summary

The HCO address search feature is currently **non-functional** due to:

1. **CMS Provider API** - Primary source failing with "Column not found" errors
2. **DuckDuckGo Search** - Fallback source blocked by rate limiting (HTTP 202)

## Test Results

**Test Case**: PENN MEDICINE PRINCETON MEDICAL CENTER (NJ)

```
✗ CMS API Failed: Column not found (400 Bad Request)
✗ DuckDuckGo Failed: Rate limited (202 Ratelimit)
✗ Final Result: No address found
```

## Root Causes

### 1. CMS API Issues
- **Problem**: Using incorrect column/property names in queries
- **Error**: `{"message":"Column not found.","status":400}`
- **Impact**: Primary data source completely non-functional
- **Fix Required**: Need to identify correct column names from CMS dataset schema

### 2. DuckDuckGo Rate Limiting
- **Problem**: Too many requests triggering rate limits
- **Error**: `RatelimitException: 202 Ratelimit`
- **Impact**: Fallback source unreliable
- **Workaround**: Need alternative search providers or rate limit handling

## Current Implementation

### Files Modified
1. `backend/services/cms_provider_service.py` - New CMS API integration (not working)
2. `backend/services/web_search_service.py` - Updated with fallback chain
3. `backend/requirements.txt` - Added httpx dependency

### Search Flow
```
User Request
    ↓
Try CMS API (fails - column not found)
    ↓
Try DuckDuckGo (fails - rate limited)
    ↓
Return: No address found
```

## Recommended Solutions

### Option 1: Fix CMS API (Best Long-term)
**Steps:**
1. Query CMS API metadata endpoint to get correct column names
2. Update query structure in `cms_provider_service.py`
3. Test with multiple hospital names
4. Keep DuckDuckGo as fallback

**Pros:**
- Official government data source
- No rate limits
- Most reliable long-term

**Cons:**
- Requires API research and testing
- May take time to debug

### Option 2: Add Google Places API (Quick Fix)
**Steps:**
1. Sign up for Google Cloud Platform
2. Enable Places API (free tier: $200/month credit)
3. Implement as primary source
4. Keep DuckDuckGo as last resort

**Pros:**
- Proven, reliable API
- Generous free tier
- Easy to implement

**Cons:**
- Requires API key
- Costs money after free tier

### Option 3: Implement Rate Limit Handling (Temporary)
**Steps:**
1. Add exponential backoff for DuckDuckGo
2. Implement request queuing
3. Add delay between requests

**Pros:**
- No new dependencies
- Works with existing code

**Cons:**
- Slow response times
- Still unreliable
- Not a real solution

## Immediate Action Required

**The address search feature is currently broken.** You need to choose one of the solutions above to restore functionality.

**Recommended**: Pursue Option 1 (Fix CMS API) as it provides the best long-term solution with no ongoing costs or rate limits.

## Testing

To test any fixes, run:
```bash
python test_address_search.py
```

Expected output when working:
```
✓ SUCCESS - Address found!
  Hospital: PENN MEDICINE PRINCETON MEDICAL CENTER
  Address: 1 Plainsboro Road
  City: Plainsboro
  State: NJ
  ZIP: 08536