# 🔴 WEBHOOK DEBUG REPORT

**Date:** February 17, 2026  
**Issue:** Netlify form webhook not firing to n8n

## Root Cause Found ✅

**Status:** The n8n workflow is **NOT ACTIVE**

### Error Message from Webhook:
```
HTTP 404
{
  "code": 404,
  "message": "The requested webhook \"POST khja4S7lboS5kyjm\" is not registered.",
  "hint": "The workflow must be active for a production URL to run successfully. 
           You can activate the workflow using the toggle in the top-right of the editor."
}
```

## What This Means

1. **Workflow Status:** The workflow `khja4S7lboS5kyjm` exists but is **INACTIVE/PAUSED**
2. **Production URL:** Production webhooks only work when the workflow is active
3. **Impact:** All form submissions from the website are being rejected by n8n
4. **Client Experience:** Users see error or the form hangs

## How to Fix

### Option 1: Activate Workflow via n8n UI (Fastest)
1. Go to: https://enmessara.app.n8n.cloud/
2. Open workflow: `khja4S7lboS5kyjm`
3. Click the **toggle switch** in top-right to enable
4. Wait for confirmation "Workflow is now active"
5. Test the form submission again

### Option 2: Activate Workflow via API
```bash
curl -X PATCH \
  -H "X-N8N-API-KEY: [your-api-key]" \
  "https://enmessara.app.n8n.cloud/api/v1/workflows/khja4S7lboS5kyjm" \
  -d '{"active": true}'
```

## Verification Steps

After activation, test with:
```bash
curl -X POST \
  "https://enmessara.app.n8n.cloud/webhook/khja4S7lboS5kyjm" \
  -H "Content-Type: application/json" \
  -d '{"test":"data", "first-name":"Test"}'
```

Expected response: Should return the lead_payload or success message (HTTP 200)

## Secondary Issues to Check

Once workflow is active:

1. **Form doesn't have `data-validate` attribute** 
   - Current: `<form name="request-time" method="POST" data-netlify="true" ...>`
   - Need: `data-validate` to trigger JavaScript submission handler
   - Fix: Add `data-validate` attribute to the form

2. **Netlify form vs n8n webhook conflict**
   - The form has `data-netlify="true"` which sends to Netlify first
   - Then our JavaScript tries to send to n8n
   - Solution: Either remove `data-netlify` or use Netlify form notifications

## Recommended Solution

The cleanest approach:

1. **Activate the workflow** (immediate fix)
2. **Add `data-validate` to the form** in index.html
3. **Keep the webhook-based submission** (our current JavaScript approach)
4. **Remove or manage Netlify form notifications** to avoid duplication

## Next Steps

1. Check if workflow is actually active in n8n UI
2. If not active, activate it
3. Test webhook endpoint again
4. If working, test full form submission from website
5. If form still doesn't fire, add `data-validate` attribute
