# Doolittle Dentistry — Voice AI + Automation Build Config

## Build Status: MVP COMPLETE (Testing in Progress)

---

## Retell AI Agent

| Field | Value |
|-------|-------|
| **Agent Name** | Kate Doolittle |
| **Agent ID** | `agent_98b3c6ca4a9841d0c5a6fd3b13` |
| **LLM ID** | `llm_56f5b63b8b3d94d5487aabb7ad5a` |
| **Voice** | 11labs-Kate (Female) |
| **Language** | en-US |
| **Model** | GPT-4o |
| **Post-Call Analysis Model** | GPT-4o-mini |
| **Max Call Duration** | 10 minutes |
| **Phone Number** | +17252414143 |
| **Webhook URL** | `https://enmessara.app.n8n.cloud/webhook/doolittle-retell-webhook` |

### Agent Tools
| Tool | Type | Description |
|------|------|-------------|
| end_call | end_call | Ends the call (emergency 911 redirect or natural conclusion) |
| route_call | transfer_call | Cold transfer to Office Manager at +17252414143 |

### Post-Call Analysis Fields (12 fields)
| Field | Type | Description |
|-------|------|-------------|
| patient_name | string | Full patient name |
| first_name | string | First name (verified/spelled) |
| phone_number | string | Patient phone number |
| insurance_name | string | Insurance provider name |
| insurance_policy_number | string | Policy number |
| insurance_group_number | string | Group number |
| urgency_level | enum | emergency / non_emergency |
| appointment_type | enum | Cleaning / Filling / Root Canal / Other |
| upsell | boolean | Whitening upsell accepted |
| appointment_confirmed | boolean | Original time confirmed |
| rescheduled | boolean | Appointment was rescheduled |
| new_appointment_time | string | New time if rescheduled |

### Dynamic Variables (injected at call time)
| Variable | Source | Used In Agent Prompt |
|----------|--------|---------------------|
| `{{patient_name}}` | Calendar event title | Greeting & confirmation |
| `{{appointment_time}}` | Calendar event start time | Appointment confirmation |
| `{{appointment_type}}` | Calendar event title | Type-specific instructions |

---

## n8n Workflow 1: Post-Call Automation

| Field | Value |
|-------|-------|
| **Workflow Name** | Doolittle Dentistry - Retell Post-Call Automation |
| **Workflow ID** | `O326l5tva09Sij0Y` |
| **Status** | Active |
| **Production Webhook** | `https://enmessara.app.n8n.cloud/webhook/doolittle-retell-webhook` |

### Pipeline (6 nodes)
```
Retell Webhook (trigger)
  ├── Respond 200 OK (immediate HTTP 200 response)
  └── Filter call_analyzed (event filter)
        └── Build lead_payload (structured JSON extraction)
              └── Internal Summary Email (every call, CC doctor if P0)
                    └── Log to Google Sheets
```

### lead_payload Object
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
  "call_id": "...",
  "call_summary": "...",
  "upsell": "true | false"
}
```

### Email Routing
| Condition | To | CC |
|-----------|----|----|
| All calls | allen@enmessara.ai | — |
| P0 Emergency | allen@enmessara.ai | allen.e89.marcus@gmail.com (Dr. Doolittle) |

### Google Sheets
| Field | Value |
|-------|-------|
| **Sheet Name** | Doolittle Dentistry Retell Call Logs |
| **Document ID** | `1phG6XAAPNUaAMtgw23l-Mjbb-LjE46YLEVDbhOupoGw` |
| **Sheet Tab** | `gid=0` (first tab) |
| **Credential** | `hstzwLoRc4QOJVEG` (Google Sheets OAuth2) |

### Google Sheets Column Mappings
| Sheet Header | lead_payload Source |
|--------------|---------------------|
| timestamp | `={{ $json.created_at }}` |
| patient_name | `={{ $json.patient_name }}` |
| phone_number | `={{ $json.phone_number }}` |
| appointment_type | `={{ $json.appointment_type }}` |
| urgency_level | `={{ $json.urgency_level }}` |
| insurance_name | `={{ $json.insurance_name }}` |
| insurance_policy_number | `={{ $json.insurance_policy_number }}` |
| insurance_group_number | `={{ $json.insurance_group_number }}` |
| call_id | `={{ $json.call_id }}` |

---

## n8n Workflow 2: Outbound Call Trigger (Instant — Watch Channel)

| Field | Value |
|-------|-------|
| **Workflow Name** | Doolittle Dentistry 2 - Outbound via Calendar Trigger |
| **Workflow ID** | `uYAEnKqeCrzrW5YV` |
| **Status** | Active |
| **Trigger** | Google Calendar Watch Channel (instant push) |
| **Webhook URL** | `https://enmessara.app.n8n.cloud/webhook/doolittle-calendar-watch` |

### Pipeline (8 nodes)
```
Google Calendar Watch Webhook (instant trigger)
  ├── Respond 200 OK (immediate)
  └── Filter: Skip Sync Messages (ignore Google's registration pings)
        └── Fetch Recent Calendar Events (next 7 days)
              └── Filter: Appointment Events (title contains "Appointment")
                    └── Extract Patient Data (parse pipe-delimited title + normalize phone)
                          └── Filter: Has Phone Number (skip events without phone)
                                └── Retell: Initiate Outbound Call (HTTP POST to Retell API)
```

### Calendar Event Format Convention
- **Title**: `Appointment | [Patient Name] | [Appointment Type]`
- **Description**: `Phone: +1XXXXXXXXXX` or `phone_number: +1XXXXXXXXXX`
- **Time**: Actual appointment date/time

**Example:**
- Title: `Appointment | Jane Smith | Cleaning`
- Description: `Phone: +15551234567`
- Start: `2026-02-15T14:00:00`

### Phone Number Normalization (E.164)
The Extract Patient Data node strips all non-digit characters and normalizes:
- 10 digits → prepend `+1`
- 11 digits starting with `1` → prepend `+`
- Longer numbers → prepend `+`

Regex: `/(Phone|phone_number|phone)\s*:\s*([+\d\-\s()]+)/i` (case-insensitive, multiple formats)

### Retell API Call
```
POST https://api.retellai.com/v2/create-phone-call
{
  "from_number": "+17252414143",
  "to_number": "<normalized E.164 from description>",
  "override_agent_id": "agent_98b3c6ca4a9841d0c5a6fd3b13",
  "retell_llm_dynamic_variables": {
    "patient_name": "<from title>",
    "appointment_time": "<from event start>",
    "appointment_type": "<from title>"
  }
}
```

**Important:** HTTP Request body uses `JSON.stringify()` expression (not `{{ }}` template syntax) to avoid n8n v4.2 interpolation bugs.

### Calendar Fetch Configuration
```
timeMin: $now.startOf('day').toISO()
timeMax: $now.plus(7, 'days').toISO()
orderBy: startTime
returnAll: true
singleEvents: true
```

---

## n8n Utility Workflow: Register Calendar Watch

| Field | Value |
|-------|-------|
| **Workflow Name** | Doolittle - Register Calendar Watch (Utility) |
| **Workflow ID** | `j8zte3WvVPwvvEVz` |
| **Purpose** | One-click manual trigger to register a Google Calendar watch channel |
| **Watch Address** | `https://enmessara.app.n8n.cloud/webhook/doolittle-calendar-watch` |
| **Calendar Credential** | `RLxXheVb5EvaLabc` (Google Calendar OAuth2) |
| **Channel Expiry** | ~7 days — must re-register before trade show |

**Note:** Each registration requires a fresh UUID for the channel ID. Generate a new one before re-running.

---

## System Architecture (End-to-End)
```
Google Calendar (event with "Appointment" in title)
  ↓ (instant via watch channel push)
Workflow 2: Calendar Watch Webhook → Fetch Events → Filter → Extract → Retell API
  ↓
Kate Doolittle calls patient → confirms/reschedules → call ends
  ↓
Retell fires call_analyzed webhook
  ↓
Workflow 1: Webhook → Filter → lead_payload → Email → Google Sheets
```

---

## Credentials & Config Reference

| Service | Key/ID | Notes |
|---------|--------|-------|
| Retell API Key | `key_2fc6e375b443f0c154eac674f220` | Bearer token |
| Retell Agent ID | `agent_98b3c6ca4a9841d0c5a6fd3b13` | Kate Doolittle |
| Retell LLM ID | `llm_56f5b63b8b3d94d5487aabb7ad5a` | GPT-4o prompt engine |
| Retell Phone | `+17252414143` | From number for outbound |
| n8n Base URL | `https://enmessara.app.n8n.cloud` | Cloud instance |
| Workflow 1 (Post-Call) | `O326l5tva09Sij0Y` | Active |
| Workflow 2 (Outbound) | `uYAEnKqeCrzrW5YV` | Active |
| Utility (Watch Register) | `j8zte3WvVPwvvEVz` | Manual trigger |
| Google Calendar Credential | `RLxXheVb5EvaLabc` | OAuth2 |
| Google Sheets Credential | `hstzwLoRc4QOJVEG` | OAuth2 |
| Gmail Credential | `ljnLfTxRZoCe4R8Q` | OAuth2 |
| Gmail (Office Manager) | `allen@enmessara.ai` | Summary emails |
| Gmail (Doctor) | `allen.e89.marcus@gmail.com` | Emergency CC |
| Google Calendar | `allen@enmessara.ai` | Watch channel source |
| Google Sheet ID | `1phG6XAAPNUaAMtgw23l-Mjbb-LjE46YLEVDbhOupoGw` | Call logs |

---

## Manual Setup Required
1. **Gmail OAuth2** — Connect in n8n credentials ✅
2. **Google Sheets OAuth2** — Connect in n8n credentials ✅
3. **Google Calendar OAuth2** — Connect in n8n credentials ✅
4. **Google Sheet** — Created "Doolittle Dentistry Retell Call Logs" ✅
5. **Watch channel** — Re-register before trade show (expires ~7 days)
6. **Publish Retell agent** — Currently in draft mode

---

*Built by Enmessara AI — MVP Trade Show Build*
*Last Updated: February 10, 2026*
