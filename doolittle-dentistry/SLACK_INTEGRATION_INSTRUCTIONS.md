# Slack Integration Instructions - Doolittle Dentistry (Next-Gen Build)

## Overview
Add a Slack emergency alert to the Doolittle Dentistry post-call automation workflow. Slack is used ONLY for P0 (emergency) calls — not for routine summaries.

---

## Architecture Note
The current workflow sends an **internal summary email for every call** (both P0 and P2). Slack is reserved exclusively for emergencies to avoid alert fatigue.

**Current pipeline:**
```
Retell Webhook → Filter call_analyzed → Build lead_payload → Internal Summary Email → Log to Google Sheets
```

**Next-gen pipeline (with Slack):**
```
Retell Webhook → Filter call_analyzed → Build lead_payload
  ├── Internal Summary Email (every call) → Log to Google Sheets
  └── IF follow_up_priority === "P0" → Slack Emergency Alert
```

---

## Prerequisites
1. A Slack workspace with admin access
2. A dedicated channel: `#doolittle-emergencies`
3. n8n instance with Slack credentials configured

---

## Step 1: Create a Slack App & Bot Token

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Name it: `Doolittle Dentistry Bot`
4. Select your workspace
5. Navigate to **OAuth & Permissions**
6. Add the following **Bot Token Scopes**:
   - `chat:write`
   - `chat:write.public`
   - `channels:read`
7. Click **"Install to Workspace"** and authorize
8. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

---

## Step 2: Create Slack Channel

1. In Slack, create channel: `#doolittle-emergencies`
2. Invite the bot: `/invite @Doolittle Dentistry Bot`

---

## Step 3: Add Slack Credentials to n8n

1. In n8n, go to **Settings → Credentials**
2. Click **"Add Credential"** → Search for **"Slack API"**
3. Paste the Bot User OAuth Token from Step 1
4. Name it: `Doolittle Dentistry Slack Bot`
5. Test the connection

---

## Step 4: Add Nodes to the Workflow

### 4a. Add an IF Node after "Build lead_payload"
Insert an **IF** node to check for emergencies:
- Condition: `{{ $json.follow_up_priority }}` equals `P0`
- TRUE branch → Slack Emergency Alert
- The Internal Summary Email should run for ALL calls (wire it from `Build lead_payload` directly, not from the IF)

### 4b. Emergency Slack Alert (P0 only)
Add a **Slack** node on the TRUE branch of the IF node:

```
Node: Slack - P0 Emergency Alert
Channel: #doolittle-emergencies
Message Template:
---
:rotating_light: *[P0] EMERGENCY DENTAL CALL*

*Business:* {{ $json.business }}
*Patient:* {{ $json.patient_name }}
*Phone:* {{ $json.phone_number }}
*Type:* {{ $json.appointment_type }}
*Priority:* P0 — EMERGENCY
*Lead Source:* {{ $json.lead_source }}

:warning: Patient was advised to call 911. Dr. Doolittle — follow up immediately.

_Call ID: {{ $json.call_id }} | {{ $json.created_at }}_
---
```

---

## Step 5: Updated Connections

```
Build lead_payload
  ├── Internal Summary Email → Log to Google Sheets  (every call)
  └── Emergency IF Check
        └── TRUE (P0) → Slack - P0 Emergency Alert
```

---

## Step 6: Test

1. Trigger a test call via Retell with urgency_level = "emergency"
2. Verify the Slack alert fires in `#doolittle-emergencies`
3. Verify non-emergency calls do NOT trigger Slack
4. Verify internal summary email still fires for both P0 and P2 calls

---

## lead_payload Reference
The Slack node receives the `lead_payload` JSON object:
```json
{
  "lead_source": "phone",
  "business": "Doolittle Dentistry",
  "patient_name": "...",
  "phone_number": "...",
  "appointment_type": "...",
  "insurance_name": "...",
  "insurance_policy_number": "...",
  "insurance_group_number": "...",
  "urgency_level": "emergency | non_emergency",
  "follow_up_priority": "P0 | P2",
  "created_at": "ISO timestamp",
  "call_id": "..."
}
```

---

## Optional Enhancements (Future Iterations)
- **@mentions**: Tag `@dr-doolittle` or `@on-call` for P0 alerts
- **Thread replies**: Group follow-up messages about the same patient
- **Slack buttons**: Add "Call Patient Back" or "View Transcript" interactive buttons
- **Daily digest**: Post end-of-day summary to `#doolittle-call-alerts`
- **Slack → n8n**: Allow staff to trigger outbound calls via Slack slash command

---

## Credential Reference
| Service | Credential Name | Where to Get |
|---------|----------------|-------------|
| Slack Bot Token | `Doolittle Dentistry Slack Bot` | Slack App Dashboard → OAuth & Permissions |
| n8n Slack Credential | Same as above | n8n Settings → Credentials |

---

## Known Bugs & Debugging Notes (Next-Gen Reference)

### Bug 1: Google Calendar "Fetch Events" Returns Wrong Events
**Symptom:** Workflow fires from the watch channel but fetches old/recurring events (e.g., "Lunch") instead of the newly created appointment.

**Root Cause:** Using `timeMin: $now.minus(5, 'minutes')` with `orderBy: updated` queries events *occurring* in the last 5 minutes — not events *created* in the last 5 minutes. Recurring events with instances in that window get returned instead.

**Fix:** Change the Calendar node to fetch upcoming events in a wider window:
```
timeMin: $now.startOf('day').toISO()
timeMax: $now.plus(7, 'days').toISO()
orderBy: startTime
returnAll: true
singleEvents: true
```
Then rely on the downstream "Filter: Appointment Events" node to filter by title.

**Prevention:** Never use `timeMin` with a narrow relative window for event-driven workflows. The push notification tells you *something changed* but doesn't tell you *what* — so fetch broadly and filter downstream.

---

### Bug 2: HTTP Request Node Fails with `httpHeaderAuth` Credential Error
**Symptom:** The "Retell: Initiate Outbound Call" HTTP Request node throws an error about header auth credentials not being found, even though the Authorization header is hardcoded in the node.

**Root Cause:** The node was configured with `authentication: "genericCredentialType"` and `genericAuthType: "httpHeaderAuth"`, which tells n8n to look for a saved `httpHeaderAuth` credential. Since none exists (the API key is hardcoded in `headerParameters`), n8n throws an error.

**Fix:** Change the node to:
```
authentication: "noAuth"
```
And keep the `Authorization: Bearer <key>` in the `headerParameters` array. This tells n8n "I'm handling auth manually."

**Prevention:** When hardcoding API keys in headers (not using saved credentials), always set `authentication: "noAuth"`. Only use `genericCredentialType` when referencing a credential saved in n8n's credential store.

---

### Bug 3: Google Calendar Watch Channel ID Not Unique
**Symptom:** Registering a watch channel fails with `"Channel id not unique"` error.

**Root Cause:** The channel ID was already registered from a previous attempt. Google requires globally unique channel IDs per watch registration.

**Fix:** Generate a new UUID (`uuid.uuid4()`) and update the utility workflow before re-running.

**Prevention:** Always generate a fresh UUID for each watch channel registration. Consider adding a UUID generator node in the utility workflow itself.

---

*Generated for Doolittle Dentistry MVP Build — Enmessara AI*
