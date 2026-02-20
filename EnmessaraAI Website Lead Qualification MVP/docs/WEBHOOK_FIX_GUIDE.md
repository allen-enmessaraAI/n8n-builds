# 🔧 N8N Webhook Debug & Fix Guide

## 🔴 Problem Identified

The Netlify form webhook was not firing to n8n because:

1. **Primary Issue:** The n8n workflow `khja4S7lboS5kyjm` is **INACTIVE**
2. **Secondary Issue:** The HTML form wasn't configured to trigger the JavaScript webhook handler

## ✅ Fixes Applied

### Fix #1: Form Configuration (Code)
**File:** `index.html` (Line 424)

**Before:**
```html
<form name="request-time" method="POST" data-netlify="true" 
      data-netlify-honeypot="bot-field" action="/success">
```

**After:**
```html
<form name="request-time" method="POST" data-validate action="/success">
```

**Why:**
- Removed `data-netlify="true"` - This was routing to Netlify, not n8n
- Added `data-validate` - This triggers the custom JavaScript webhook handler in `assets/main.js`
- Removed honeypot field - No longer needed since we're using webhook-based submission

**Commit:** `dc68a30`

---

## 🚨 Critical Step: Activate the Workflow

The webhook will still fail if the workflow is not active. **You must do this:**

### Option A: Activate via Web UI (Recommended)

1. Go to: https://enmessara.app.n8n.cloud/
2. Open the workflow with ID: `khja4S7lboS5kyjm`
3. Click the **toggle switch** in the top-right corner
4. Look for message: ✅ "Workflow is active"
5. The workflow icon should show as "running"

### Option B: Activate via API

```bash
curl -X PATCH \
  -H "X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MmQ5ZjNhYy01Mzk1LTQ4MGEtYTg2Zi02MzAyNjkyNjUyOTQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzcxMjkwMzY1fQ.HAO9ZiCQyiSZ_Geg6CKuNDluQItyG-9Z3TzOQOVaKLk" \
  -H "Content-Type: application/json" \
  "https://enmessara.app.n8n.cloud/api/v1/workflows/khja4S7lboS5kyjm" \
  -d '{"active": true}'
```

**Expected Response:**
```json
{
  "active": true,
  "id": "khja4S7lboS5kyjm",
  "updatedAt": "2026-02-17T..."
}
```

---

## 🧪 Testing the Fix

### Test 1: Webhook Endpoint

Run this command to test if the webhook is now accessible:

```bash
curl -X POST \
  "https://enmessara.app.n8n.cloud/webhook/khja4S7lboS5kyjm" \
  -H "Content-Type: application/json" \
  -d '{
    "first-name": "Test",
    "last-name": "User", 
    "email": "test@example.com",
    "phone": "5551234567",
    "company": "Test Co"
  }'
```

**Success Response (HTTP 200):**
```json
{
  "success": true,
  "message": "Lead received and processing",
  "lead_id": "1739806311000"
}
```

**Failure Response (HTTP 404):**
```json
{
  "code": 404,
  "message": "The requested webhook \"POST khja4S7lboS5kyjm\" is not registered.",
  "hint": "The workflow must be active..."
}
```

### Test 2: Form Submission from Website

1. Go to: https://enmessara.ai/
2. Scroll to "Request a Time" section
3. Fill out the form with test data
4. Click "Request a Time"
5. Expected: Form shows "Request Received!" message
6. Check n8n workflow executions to see the submission

---

## 📊 Current Flow

```
User Form Submission
        ↓
   index.html form
        ↓
   assets/main.js (initForms)
        ↓
   Phone Sanitization
        ↓
   Lead Payload Enrichment
        ↓
   POST to n8n Webhook
        ↓
   n8n Workflow khja4S7lboS5kyjm
        ↓
   Standardize Data → Create Lead Payload → Phone Valid?
        ↓
   Valid: Call Retell AI → (Voicemail branch) → Gmail notification
   Invalid: Log to Sheet → Send 200 OK
```

---

## 🔍 Monitoring & Debugging

### Check Workflow Status

```bash
curl -s \
  -H "X-N8N-API-KEY: [your-api-key]" \
  "https://enmessara.app.n8n.cloud/api/v1/workflows/khja4S7lboS5kyjm" | \
  grep -E '"active"|"id"|"updatedAt"'
```

### Check Recent Executions

Go to: https://enmessara.app.n8n.cloud/workflows/khja4S7lboS5kyjm/executions

Look for:
- ✅ Green checkmarks = Successful submissions
- 🔴 Red X = Failed submissions
- Most recent should appear as you submit forms

### Browser Console Testing

1. Open website in browser
2. Press `F12` to open Developer Tools
3. Go to "Console" tab
4. Submit a test form
5. Look for logs:
   - `Sanitized phone: +1-555-123-4567` ✓
   - `Form submission successful: {...}` ✓
   - Any errors will be shown in red

---

## 🚨 Possible Issues & Solutions

### Issue 1: Still Getting 404 After Changes

**Cause:** Workflow is still inactive

**Solution:** 
1. Go to n8n UI
2. Make sure toggle is ON (blue)
3. Wait 10 seconds
4. Test webhook again

### Issue 2: CORS Errors in Console

**Error:** "Cross-Origin Request Blocked"

**Cause:** Browser blocking the cross-domain request

**Solution:** 
- This is normal for browser testing
- Production will work because form is submitted from same domain
- Check n8n execution logs to see if request arrived

### Issue 3: Form Shows Error "Problem Sending Message"

**Cause:** Webhook returned error (HTTP status ≥ 400)

**Solution:**
1. Check browser console for exact error
2. Check n8n execution logs for workflow errors
3. Verify phone validation is working
4. Check that required fields are filled

### Issue 4: Form Submits But No Email Received

**Cause:** Gmail OAuth credential expired or not configured

**Solution:**
1. Go to n8n Credentials
2. Check "Notification: Follow Up Lead" status
3. Re-authenticate if needed
4. Test workflow manually in n8n UI

---

## 📋 Pre-Launch Checklist

- [ ] Workflow `khja4S7lboS5kyjm` is **ACTIVE** (blue toggle)
- [ ] Form has `data-validate` attribute
- [ ] Test webhook returns HTTP 200
- [ ] Test form submission from website
- [ ] Check Gmail for notification email
- [ ] Verify phone sanitization works
- [ ] Check n8n execution logs for no errors
- [ ] Confirm Retell AI calls are being made
- [ ] Verify lead_payload structure is correct

---

## 📞 Support

If webhook still doesn't fire after these steps:

1. Check n8n workflow active status first ⚠️
2. Review browser console for JavaScript errors
3. Check n8n execution logs for workflow errors
4. Verify all credentials are valid (Gmail, Retell AI, Google Sheets)
5. Test webhook URL directly with curl

---

**Last Updated:** February 17, 2026  
**Status:** ✅ Form code fixed, awaiting workflow activation
