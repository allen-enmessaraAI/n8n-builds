# N8N Netlify Form Integration Guide

**Created:** February 16, 2026  
**Workflow ID:** `khja4S7lboS5kyjm`  
**N8N Instance:** enmessara.app.n8n.cloud

---

## Architecture Overview

### Two Integration Paths

#### **Path A: Netlify Form Submission Notifications** (Primary)
Used for: "Request a Time" form (index.html, panel-form)

```
User submits form → Netlify detects submission → Netlify HTTP POST to n8n → n8n webhook receives data
```

**Advantages:**
- Automatic form detection (no extra JS needed)
- Built-in spam filtering
- Netlify handles validation
- Works even if client-side JS fails

#### **Path B: Direct AJAX to n8n Webhook** (Fallback)
Used for: Contact form (contact.html)

```
User submits form → Custom JS validation → AJAX POST to n8n webhook → n8n webhook receives data
```

**Advantages:**
- Fine-grained control over UX
- Real-time validation feedback
- Custom error handling

---

## Step-by-Step Implementation

### **STEP 1: Get Your N8N Webhook URL**

#### 1a. Access n8n Instance
- Go to: https://enmessara.app.n8n.cloud
- Sign in with your credentials

#### 1b. Open Workflow `khja4S7lboS5kyjm`
- Navigate to **Workflows** → Find `khja4S7lboS5kyjm`
- Open the workflow

#### 1c. Configure Webhook Trigger
- Locate the **Webhook node** (should be the trigger)
- Configuration required:
  - **HTTP Method:** POST
  - **Authentication:** Use the API key provided
  - Copy the **Webhook URL** generated (format: `https://enmessara.app.n8n.cloud/webhook/...`)

**API Key Reference:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MmQ5ZjNhYy01Mzk1LTQ4MGEtYTg2Zi02MzAyNjkyNjUyOTQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzcxMjkwMzY1fQ.HAO9ZiCQyiSZ_Geg6CKuNDluQItyG-9Z3TzOQOVaKLk
```

---

### **STEP 2: Configure Netlify Form Submission Notifications**

#### 2a. Access Netlify Dashboard
- Go to: https://app.netlify.com
- Select your site: `enmessara-website`

#### 2b. Enable Form Detection (if not already enabled)
- Navigate to: **Forms** → **Usage and Configuration**
- Verify **Form Detection** is enabled
- If disabled, click **Enable form detection** and redeploy

#### 2c. Add Form Notification
- Go to: **Site Settings** → **Forms** → **Form notifications**
  - OR: **Notifications** → **Form submission notifications** → **Add notification**

#### 2d. Select Notification Type
- Choose: **HTTP POST request** (Webhook)

#### 2e. Configure Webhook Details
- **URL:** Your n8n webhook URL from Step 1c
- **Secret token (optional):** Leave empty for now; can add later for JWS signature validation
- **Form name (optional):** Select `request-time` to receive only from that form
  - OR leave empty to receive all form submissions

#### 2f. Payload Structure
Netlify will send a POST request with this payload structure:

```json
{
  "id": "submission-id-12345",
  "number": 1,
  "title": null,
  "email": null,
  "name": "request-time",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1-555-123-4567",
  "company": "Acme Corp",
  "website": "https://acmecorp.com",
  "role": "CTO",
  "company_size": "21-100",
  "budget": "Yes",
  "help_request": "Help with automation",
  "improvement_goal": "Lead Generation/Sales",
  "created_at": "2026-02-16T12:34:56Z",
  "summary": "New submission from john@example.com"
}
```

#### 2g. Save Configuration
- Click **Save** or **Create**
- Netlify will display confirmation

---

### **STEP 3: Update Contact Form for Direct n8n Submission**

For the contact form (contact.html), we'll enhance the existing AJAX implementation:

#### 3a. Update main.js webhook URL

**Current state:** Form sends to `https://enmessara.app.n8n.cloud/webhook/enmessara-request-time`

**New configuration:** Update with your n8n webhook URL from Step 1c

See [Updates Required](#updates-required) section below.

---

### **STEP 4: Validate Both Forms**

#### 4a. Request Time Form (Netlify)
1. Visit https://enmessara.ai (or localhost if testing)
2. Scroll to **"Book a Discovery Call"** section
3. Click **"Request a Time"** tab
4. Fill in all required fields
5. Click **"Request a Time"** button
6. Verify success message appears
7. Check n8n workflow to confirm data received

#### 4b. Contact Form (Direct)
1. Visit https://enmessara.ai/contact.html
2. Fill in all required fields
3. Click **"Send Message"** button
4. Verify success message appears
5. Check n8n workflow to confirm data received

---

## Updates Required

### File: `assets/main.js`

**Current Code (lines ~120-140):**
```javascript
const WEBHOOK_URL = 'https://enmessara.app.n8n.cloud/webhook/enmessara-request-time';
```

**Update to:**
```javascript
// Contact form sends directly to n8n webhook
const CONTACT_WEBHOOK_URL = 'https://enmessara.app.n8n.cloud/webhook/khja4S7lboS5kyjm';
```

**Additional Headers to Add:**
```javascript
headers: {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2MmQ5ZjNhYy01Mzk1LTQ4MGEtYTg2Zi02MzAyNjkyNjUyOTQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzcxMjkwMzY1fQ.HAO9ZiCQyiSZ_Geg6CKuNDluQItyG-9Z3TzOQOVaKLk'
}
```

---

## Troubleshooting Checklist

### If Netlify Form Notifications Don't Fire:

- [ ] Verify form has `data-netlify="true"` attribute
- [ ] Verify form has unique `name` attribute
- [ ] Redeploy site after enabling form detection
- [ ] Check Netlify **Forms** → **Submissions** to see if form is being captured
- [ ] Verify webhook URL in notification settings is correct and accessible
- [ ] Check n8n webhook logs for rejected requests
- [ ] Validate form fields match n8n workflow expectations

### If Contact Form Direct Submission Fails:

- [ ] Check browser console for fetch errors
- [ ] Verify webhook URL is correct
- [ ] Test webhook URL directly in Postman/curl
- [ ] Check n8n workflow is active and listening
- [ ] Verify API key hasn't expired
- [ ] Check CORS settings (if applicable)
- [ ] Monitor n8n webhook node for incoming requests

### Common Errors:

| Error | Cause | Solution |
|-------|-------|----------|
| 404 on webhook URL | Invalid webhook URL | Verify URL in n8n workflow |
| 401 Unauthorized | Missing/invalid API key | Regenerate API key in n8n |
| 403 Forbidden | CORS policy blocked request | Contact n8n support or adjust CORS settings |
| Submission not appearing in n8n | Form data format mismatch | Check field names match n8n workflow inputs |
| Success but no data | Webhook received but parsing failed | Verify JSON payload structure in n8n |

---

## API Key Security Notes

⚠️ **Important:** The API key is currently embedded in the code. For production:

1. **Option 1:** Use environment variables (Netlify build settings)
   ```
   NETLIFY_N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   
2. **Option 2:** Use Netlify Functions as proxy
   - Create a serverless function that adds the API key server-side
   - Client sends to function, function forwards to n8n with auth

3. **Option 3:** Use Netlify Secrets
   - Store in Netlify's secure secrets management

For now, webhook URLs typically don't require authentication if the URL itself is secret.

---

## Testing Payload Examples

### Netlify Form Submission Payload:
```json
{
  "id": "abc123",
  "number": 1,
  "name": "request-time",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@company.com",
  "phone": "+1-555-987-6543",
  "company": "Tech Corp",
  "website": "https://techcorp.com",
  "role": "VP Operations",
  "company_size": "101-500",
  "budget": "Yes",
  "help_request": "Looking to automate lead qualification",
  "improvement_goal": "Lead Generation/Sales",
  "created_at": "2026-02-16T14:30:00Z"
}
```

### Contact Form Direct Payload:
```json
{
  "name": "John Manager",
  "email": "john@example.com",
  "phone": "+1-555-111-2222",
  "company": "Example Inc",
  "subject": "project",
  "message": "We'd like to discuss a new project..."
}
```

---

## Workflow Activation Checklist

- [ ] N8N workflow khja4S7lboS5kyjm is **ACTIVE** (not inactive/draft)
- [ ] Webhook node has correct HTTP method (POST)
- [ ] Webhook node is connected to downstream nodes
- [ ] Netlify form notification uses correct webhook URL
- [ ] Form fields are properly mapped in n8n workflow
- [ ] Error handling configured in n8n (error emails, logs, etc.)
- [ ] Test submission successful from both forms
- [ ] Deployment successful (git push completed)

---

## Support & Debugging

### Check N8N Logs:
1. Open workflow `khja4S7lboS5kyjm`
2. Click **Executions** tab
3. Look for recent requests
4. Check webhook node logs for errors

### Check Netlify Form Submissions:
1. Go to site dashboard
2. Click **Forms**
3. Click **Submissions**
4. Filter by form name
5. Verify submission data captured

### Manual Webhook Test:
```bash
curl -X POST \
  'https://enmessara.app.n8n.cloud/webhook/khja4S7lboS5kyjm' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "test-user",
    "email": "test@example.com",
    "phone": "555-1234",
    "company": "Test Corp",
    "subject": "testing",
    "message": "Test message"
  }'
```

---

## Next Steps

1. **Verify n8n webhook is active and accessible**
   - Test with curl command above
   
2. **Configure Netlify notification**
   - Add HTTP POST notification to form
   
3. **Update contact form JavaScript** (if needed)
   - Ensure webhook URL matches n8n instance
   
4. **Deploy to production**
   - Commit changes to git
   - Deploy to Netlify
   
5. **Test both forms end-to-end**
   - Fill and submit each form
   - Verify data arrives in n8n
   - Check workflow executions
   
6. **Monitor for issues**
   - Watch form submission errors
   - Review n8n execution logs daily
   - Adjust error notifications as needed

