# N8N Form Integration - Test Checklist

**Test Date:** February 16, 2026  
**Tester:** [Your Name]  
**Environment:** [Development/Staging/Production]

---

## Pre-Flight Checks ✓

### N8N Setup
- [ ] N8N workflow `khja4S7lboS5kyjm` is **ACTIVE** (not draft/inactive)
- [ ] Webhook node has HTTP Method set to **POST**
- [ ] Webhook node is properly connected to downstream nodes
- [ ] Webhook URL generated and accessible: 
  ```
  https://enmessara.app.n8n.cloud/webhook/khja4S7lboS5kyjm
  ```
- [ ] Test webhook URL with curl (see below)

### Netlify Setup
- [ ] Form detection is **ENABLED** in Netlify Forms settings
- [ ] Site has been redeployed since enabling form detection
- [ ] Webhook notification created and pointing to n8n webhook URL
- [ ] Form name: `request-time` is correctly configured
- [ ] Netlify Forms dashboard shows form capture enabled

### Code Changes
- [ ] `assets/main.js` updated with correct webhook URL
- [ ] Webhook URL matches n8n instance: `khja4S7lboS5kyjm`
- [ ] Changes committed to git
- [ ] Changes deployed to Netlify

---

## Test 1: N8N Webhook Connectivity

**Goal:** Verify n8n webhook is accessible and receiving POST requests

### 1a. Manual CURL Test
```bash
curl -X POST \
  'https://enmessara.app.n8n.cloud/webhook/khja4S7lboS5kyjm' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+1-555-0000",
    "company": "Test Corp",
    "subject": "test",
    "message": "This is a test message"
  }'
```

**Expected Result:**
- ✓ HTTP 200 response
- ✓ Response body contains success indicator
- ✓ No 404, 401, or 403 errors

**Result:** ☐ PASS ☐ FAIL  
**Error (if any):** ___________________________

### 1b. Check N8N Execution Logs
1. Open n8n workflow `khja4S7lboS5kyjm`
2. Click **Executions** tab
3. Look for execution from CURL test
4. Click to view details

**Expected:**
- ✓ Execution appears in logs
- ✓ Status shows "success" or similar
- ✓ Webhook node shows data received

**Result:** ☐ PASS ☐ FAIL  
**Details:** ___________________________

---

## Test 2: Contact Form Direct Submission (contact.html)

**Goal:** Verify contact form sends data directly to n8n webhook

### 2a. Fill and Submit Contact Form
1. Navigate to https://enmessara.ai/contact.html (or localhost)
2. Fill in form with test data:
   - **Name:** Test Contact User
   - **Email:** contact-test@enmessara-test.com
   - **Phone:** +1-555-1111
   - **Company:** Test Company
   - **Subject:** New Project Inquiry (dropdown)
   - **Message:** This is a test message from the contact form

3. Click "Send Message" button
4. Observe button changes to "Sending..."

**Result:** ☐ PASS ☐ FAIL

### 2b. Verify Success Message
- [ ] Form hides after submission
- [ ] "Message Sent!" success message appears
- [ ] Success message shows: "Thank you for reaching out. We'll get back to you within 1 business day."

**Result:** ☐ PASS ☐ FAIL

### 2c. Check Browser Console
1. Open Developer Tools (F12)
2. Go to **Console** tab
3. Check for any error messages

**Expected:**
- ✓ No red error messages
- ✓ Console shows success log or is clean
- ✓ Network tab shows POST 200 to webhook URL

**Result:** ☐ PASS ☐ FAIL  
**Console Errors:** ___________________________

### 2d. Check N8N Logs
1. Open n8n workflow `khja4S7lboS5kyjm`
2. Click **Executions** tab
3. Look for recent execution with contact form data
4. Verify data structure matches sent payload

**Expected Data Fields:**
- ✓ name: "Test Contact User"
- ✓ email: "contact-test@enmessara-test.com"
- ✓ phone: "+1-555-1111"
- ✓ company: "Test Company"
- ✓ subject: "project"
- ✓ message: "This is a test message from the contact form"
- ✓ submittedAt: (timestamp)
- ✓ formType: "contact" or form name

**Result:** ☐ PASS ☐ FAIL  
**Received Data:** ___________________________

---

## Test 3: Netlify Form Direct Submission (index.html - Request Form)

**Goal:** Verify Netlify captures form submission and forwards to n8n

### 3a. Fill and Submit Request Form
1. Navigate to https://enmessara.ai (or localhost)
2. Scroll to "Book a Discovery Call" section
3. Click "Request a Time" tab
4. Fill in form with test data:
   - **First Name:** Netlify
   - **Last Name:** Test
   - **Email:** netlify-test@enmessara-test.com
   - **Phone:** +1-555-2222
   - **Company:** Netlify Test Corp
   - **Website:** https://netlify-test.example.com
   - **Your Role:** Test Manager
   - **Company Size:** 21-100 employees
   - **Budget:** Yes
   - **How can we help:** Testing the integration
   - **What are you hoping to improve:** Lead Generation/Sales

5. Click "Request a Time" button

**Result:** ☐ PASS ☐ FAIL

### 3b. Verify Success Message
- [ ] Form submission succeeds
- [ ] "Request Received!" message appears
- [ ] Message shows: "We'll get back to you within 1 business day with available times."

**Result:** ☐ PASS ☐ FAIL

### 3c. Check Netlify Forms Dashboard
1. Go to Netlify site dashboard
2. Click **Forms** → **Submissions**
3. Filter by form: `request-time`
4. Look for submission with Netlify Test's data

**Expected:**
- ✓ Submission appears in list
- ✓ Email field shows: netlify-test@enmessara-test.com
- ✓ Submission status: "Verified" or "Confirmed"
- ✓ Submission contains all form fields

**Result:** ☐ PASS ☐ FAIL  
**Netlify Submission ID:** ___________________________

### 3d. Check N8N Logs
1. Open n8n workflow `khja4S7lboS5kyjm`
2. Click **Executions** tab
3. Look for execution from Netlify notification (within 5-10 seconds of form submission)

**Expected Data Fields:**
- ✓ first_name: "Netlify"
- ✓ last_name: "Test"
- ✓ email: "netlify-test@enmessara-test.com"
- ✓ phone: "+1-555-2222"
- ✓ company: "Netlify Test Corp"
- ✓ website: "https://netlify-test.example.com"
- ✓ role: "Test Manager"
- ✓ company_size: "21-100"
- ✓ budget: "Yes"
- ✓ help_request: "Testing the integration"
- ✓ improvement_goal: "Lead Generation/Sales"
- ✓ created_at: (timestamp from Netlify)

**Result:** ☐ PASS ☐ FAIL  
**Received Data:** ___________________________

---

## Test 4: Error Handling & Edge Cases

### 4a. Contact Form - Missing Required Fields
1. Go to contact form (contact.html)
2. Leave required fields empty
3. Try to submit (without filling name, email, etc.)

**Expected:**
- ✓ Form validation prevents submission
- ✓ Required fields highlighted in red
- ✓ Error messages displayed
- ✓ No webhook call made

**Result:** ☐ PASS ☐ FAIL

### 4b. Contact Form - Invalid Email
1. Go to contact form
2. Enter invalid email: "notanemail"
3. Try to submit

**Expected:**
- ✓ Email field highlighted with error
- ✓ Form submission prevented
- ✓ Error message shown

**Result:** ☐ PASS ☐ FAIL

### 4c. Netlify Form - Empty Required Fields
1. Go to booking section (Request Form)
2. Leave required fields empty
3. Try to submit

**Expected:**
- ✓ Browser HTML5 validation prevents submission
- ✓ Error messages shown ("This field is required" or similar)
- ✓ No submission to Netlify or n8n

**Result:** ☐ PASS ☐ FAIL

### 4d. Special Characters in Fields
1. Fill contact form with special characters in message:
   - Test with: `" ' < > & ! @ # $ % ^ * ( )`
2. Submit form
3. Verify data arrives in n8n correctly escaped

**Expected:**
- ✓ Form submits successfully
- ✓ Characters properly encoded/escaped in JSON
- ✓ N8N receives and displays correctly

**Result:** ☐ PASS ☐ FAIL

---

## Test 5: Data Delivery & Workflow Execution

### 5a. Verify N8N Processes Contact Form Data
1. Submit contact form with unique test data
2. Check n8n execution
3. Verify workflow executes downstream nodes (if configured)

**Expected:**
- ✓ Webhook node triggers
- ✓ Data flows to next node in workflow
- ✓ No errors in execution
- ✓ Final output shows successful processing

**Result:** ☐ PASS ☐ FAIL  
**Workflow Status:** ___________________________

### 5b. Verify N8N Processes Netlify Form Data
1. Submit Netlify request form with unique test data
2. Check n8n execution (may take 5-10 seconds)
3. Verify workflow executes

**Expected:**
- ✓ Webhook node triggers from Netlify notification
- ✓ All Netlify form fields received
- ✓ Workflow completes without errors

**Result:** ☐ PASS ☐ FAIL  
**Execution Duration:** ___________________________

### 5c. Check for Data Consistency
Compare data in:
1. Form submission (what user entered)
2. Netlify dashboard (what Netlify captured)
3. N8N execution logs (what webhook received)

**Expected:**
- ✓ All three match
- ✓ No data loss or corruption
- ✓ Timestamps consistent

**Result:** ☐ PASS ☐ FAIL

---

## Test 6: Multiple Submissions

### 6a. Rapid Submissions
1. Submit contact form
2. Immediately submit again (before page reloads)
3. Repeat 3-5 times

**Expected:**
- ✓ All submissions succeed
- ✓ Each generates unique submission ID
- ✓ N8N receives all requests
- ✓ No rate limiting or blocking

**Result:** ☐ PASS ☐ FAIL  
**Submissions Received:** ___ / ___

### 6b. High Volume Test (Optional)
1. Submit contact form 20+ times (automated or manual)
2. Monitor n8n for successful processing

**Expected:**
- ✓ All submissions received
- ✓ No dropped requests
- ✓ N8N workflow completes all executions

**Result:** ☐ PASS ☐ FAIL

---

## Test 7: Browser Compatibility

### 7a. Chrome/Chromium
- **Environment:** [version]
- **Test Result:** ☐ PASS ☐ FAIL
- **Issues:** ___________________________

### 7b. Firefox
- **Environment:** [version]
- **Test Result:** ☐ PASS ☐ FAIL
- **Issues:** ___________________________

### 7c. Safari
- **Environment:** [version]
- **Test Result:** ☐ PASS ☐ FAIL
- **Issues:** ___________________________

### 7d. Mobile (iOS Safari)
- **Device:** [model]
- **Test Result:** ☐ PASS ☐ FAIL
- **Issues:** ___________________________

### 7e. Mobile (Android Chrome)
- **Device:** [model]
- **Test Result:** ☐ PASS ☐ FAIL
- **Issues:** ___________________________

---

## Test 8: Network Conditions

### 8a. Slow Network (2G Throttling)
1. Open DevTools Network tab
2. Set throttling to "Slow 2G"
3. Submit contact form
4. Observe timeout or slow response

**Expected:**
- ✓ Form eventually succeeds
- ✓ Timeout threshold reasonable (>30 seconds suggests issue)
- ✓ Error handling shows if timeout occurs

**Result:** ☐ PASS ☐ FAIL

### 8b. Offline to Online Recovery
1. Enable airplane mode or offline mode
2. Try to submit form
3. Disable offline mode
4. Retry submission

**Expected:**
- ✓ Offline: Error message shown
- ✓ Online: Resubmission works
- ✓ No silent failures

**Result:** ☐ PASS ☐ FAIL

---

## Production Deployment Checklist

Before deploying to production:

- [ ] All tests pass
- [ ] N8N webhook URL is finalized and stable
- [ ] Netlify form notification configured correctly
- [ ] Error handling messages are user-friendly
- [ ] Contact email is correct (hello@enmessara.ai)
- [ ] Success messages are professional
- [ ] Forms have appropriate field validation
- [ ] GDPR/privacy disclaimers in place (if needed)
- [ ] Rate limiting configured in N8N (if needed)
- [ ] Monitoring/alerting set up for failed submissions
- [ ] Documentation updated for support team
- [ ] Client/team notified of launch
- [ ] A/B testing planned (if applicable)

---

## Issues Found & Resolutions

### Issue #1: [Description]
- **Severity:** ☐ Critical ☐ High ☐ Medium ☐ Low
- **Root Cause:** ___________________________
- **Resolution:** ___________________________
- **Status:** ☐ Fixed ☐ In Progress ☐ Blocked
- **Test Result After Fix:** ☐ PASS ☐ FAIL

### Issue #2: [Description]
- **Severity:** ☐ Critical ☐ High ☐ Medium ☐ Low
- **Root Cause:** ___________________________
- **Resolution:** ___________________________
- **Status:** ☐ Fixed ☐ In Progress ☐ Blocked
- **Test Result After Fix:** ☐ PASS ☐ FAIL

### Issue #3: [Description]
- **Severity:** ☐ Critical ☐ High ☐ Medium ☐ Low
- **Root Cause:** ___________________________
- **Resolution:** ___________________________
- **Status:** ☐ Fixed ☐ In Progress ☐ Blocked
- **Test Result After Fix:** ☐ PASS ☐ FAIL

---

## Summary

| Category | Tests | Passed | Failed | Notes |
|----------|-------|--------|--------|-------|
| N8N Connectivity | 2 | ☐ | ☐ | |
| Contact Form | 4 | ☐ | ☐ | |
| Netlify Form | 4 | ☐ | ☐ | |
| Error Handling | 4 | ☐ | ☐ | |
| Data Delivery | 3 | ☐ | ☐ | |
| Multiple Submissions | 2 | ☐ | ☐ | |
| Browser Compatibility | 5 | ☐ | ☐ | |
| Network Conditions | 2 | ☐ | ☐ | |
| **TOTAL** | **26** | **☐** | **☐** | |

**Overall Status:** ☐ ALL PASS ☐ SOME FAILURES ☐ CRITICAL ISSUES

**Approved for Production:** ☐ YES ☐ NO ☐ CONDITIONAL

**Approval Date:** _________________  
**Approved By:** _________________  
**Notes:** ___________________________

---

## Sign-Off

- [ ] All tests completed
- [ ] Issues documented
- [ ] Resolutions verified
- [ ] Team notified
- [ ] Ready for production deployment

**Tester Name:** _________________  
**Tester Signature:** _________________  
**Date:** _________________  
**Time:** _________________

