# Earnhardt Auto Shop - Voice AI + Automation Build Config

## Build Status: ACTIVE (Production Ready)

---

## Retell AI Agent

| Field | Value |
|-------|-------|
| **Agent Name** | Dale |
| **Agent ID** | `agent_1366e6adc7ed1285dfe778fcee` |
| **LLM ID** | `llm_f9dd69c5fff756372d4c89f0a6d4` |
| **Voice** | 11labs-Adrian (Male) |
| **Language** | multi (EN/ES auto-detect for both STT and LLM) |
| **Model** | GPT-4o |
| **Post-Call Analysis Model** | GPT-4o-mini |
| **Max Call Duration** | 10 minutes |
| **Phone Number** | +17252289486 |
| **Webhook URL** | `https://enmessara.app.n8n.cloud/webhook/earnhardt-retell-webhook` |

### Agent Tools
| Tool | Type | Description |
|------|------|-------------|
| end_call | end_call | Ends call naturally or on request |
| route_call | transfer_call | Cold transfer to Service Manager at +17252491032 |
| check_calendar | custom | Calls n8n webhook to get available appointment slots |

### Post-Call Analysis Fields (13 fields)
| Field | Type | Description |
|-------|------|-------------|
| first_name | string | Customer first name (verified/spelled) |
| year | string | Vehicle year (4-digit) |
| car_make_model | string | Vehicle make and model |
| phone_number | string | Customer phone number |
| service_type | string | Oil Change / Brake Service / Tires / Body Work / Repairs |
| mileage | string | Current vehicle mileage |
| text_optin | boolean | Text message opt-in |
| insurance_name | string | Insurance provider (Body Work/Repairs) |
| insurance_policy_number | string | Policy number (Body Work/Repairs) |
| claim_agent_name | string | Claims agent name or N/A |
| claim_agent_email | string | Claims agent email or N/A |
| claim_agent_number | string | Claims agent phone or N/A |
| upsell_interested | boolean | Radiator flush upsell interest (Tires + >30k miles) |

### Dynamic Variables (injected at call time)
| Variable | Source | Used In Agent Prompt |
|----------|--------|---------------------|
| `{{customer_name}}` | Calendar event title | Greeting & confirmation |
| `{{appointment_time}}` | Calendar event start time | Appointment confirmation |
| `{{appointment_type}}` | Calendar event title | Type-specific instructions |

---

## n8n Workflow 1: Post-Call Automation

| Field | Value |
|-------|-------|
| **Workflow Name** | Earnhardt Auto Shop - Retell Post-Call Automation |
| **Workflow ID** | `iEbeP2uQtxMQxlqy` |
| **Status** | Active |
| **Production Webhook** | `https://enmessara.app.n8n.cloud/webhook/earnhardt-retell-webhook` |

### Pipeline (8 nodes)
```
Retell Webhook (POST trigger)
  +--> Respond 200 OK (immediate)
  +--> Filter call_analyzed (event filter)
        +--> Build lead_payload + Score (Code node: extract + score)
              +--> IF car_age > 3
                    |-- TRUE --> Gmail - Sales Manager (Trade-In Alert)
                    |              +--> Log to Google Sheets
                    |-- FALSE --> Gmail - Service Manager (Summary)
                                   +--> Log to Google Sheets
```

### Qualification Scoring Formula
| Factor | Points |
|--------|--------|
| Car age 10+ years | 40 |
| Car age 7-9 years | 30 |
| Car age 4-6 years | 20 |
| Car age 0-3 years | 5 |
| Mileage 100k+ | 30 |
| Mileage 75-100k | 20 |
| Mileage 50-75k | 10 |
| Mileage <50k | 5 |
| Body Work/Repairs | 20 |
| Brake Service | 10 |
| Tires | 5 |
| Oil Change | 0 |
| Upsell accepted | 10 |

### Email Routing
| Condition | To | Subject Pattern |
|-----------|----|----|
| car_age > 3 | allen.e89.marcus@gmail.com (Sales) | [HIGH PRIORITY] Trade-In Lead - {name} |
| car_age <= 3 | allen@enmessara.ai (Service) | Service Confirmation - {name} |

---

## n8n Workflow: Calendar Availability Helper

| Field | Value |
|-------|-------|
| **Workflow Name** | Earnhardt Auto Shop - Calendar Availability Helper |
| **Workflow ID** | `VxK2zcht3OctrDfm` |
| **Status** | Active |
| **Production Webhook** | `https://enmessara.app.n8n.cloud/webhook/earnhardt-calendar-check` |

### Pipeline (4 nodes)
```
Calendar Check Webhook (POST)
  +--> Fetch Calendar Events (next 7 days)
       +--> Find Available Slots (Code: 3 open 60-min blocks, Mon-Sat 8am-5pm)
            +--> Return Available Slots (JSON response)
```

### Response Format
```json
{
  "available_slots": [
    { "datetime": "2026-02-16T10:00:00.000Z", "display": "Monday, February 16 at 10:00 AM" },
    { "datetime": "2026-02-16T14:00:00.000Z", "display": "Monday, February 16 at 2:00 PM" },
    { "datetime": "2026-02-17T09:00:00.000Z", "display": "Tuesday, February 17 at 9:00 AM" }
  ]
}
```

---

## n8n Workflow 2: Outbound Call Trigger

| Field | Value |
|-------|-------|
| **Workflow Name** | Earnhardt Auto Shop - Outbound via Calendar Trigger |
| **Workflow ID** | `KJk3TuaZmlqd0j9c` |
| **Status** | Active |
| **Production Webhook** | `https://enmessara.app.n8n.cloud/webhook/earnhardt-calendar-watch` |

### Pipeline (8 nodes)
```
Calendar Watch Webhook (instant trigger from Google)
  +--> Respond 200 OK
  +--> Skip Sync Messages (filter Google registration pings)
       +--> Fetch Calendar Events (next 7 days)
            +--> Filter: title contains "Appointment"
                 +--> Extract Customer Data (parse pipe-delimited title)
                      +--> Has Phone Number? (filter empty)
                           +--> Retell: Initiate Outbound Call
```

### Calendar Event Format Convention
- **Title**: `Appointment | [Customer Name] | [Service Type]`
- **Description**: `Phone: +1XXXXXXXXXX`
- **Example**: Title: `Appointment | Jane Smith | Oil Change`, Description: `Phone: +17255551234`

### Retell API Call
```json
{
  "from_number": "+17252289486",
  "to_number": "<from calendar description>",
  "override_agent_id": "agent_1366e6adc7ed1285dfe778fcee",
  "retell_llm_dynamic_variables": {
    "customer_name": "<from title>",
    "appointment_time": "<from event start>",
    "appointment_type": "<from title>"
  }
}
```

---

## n8n Utility Workflow: Register Calendar Watch

| Field | Value |
|-------|-------|
| **Workflow Name** | Earnhardt Auto - Register Calendar Watch (Utility) |
| **Workflow ID** | `rzjOerqQJDoyNbkn` |
| **Status** | Inactive (manual trigger only) |
| **Watch Address** | `https://enmessara.app.n8n.cloud/webhook/earnhardt-calendar-watch` |
| **Channel Expiry** | ~7 days (re-register before expiry) |

---

## Google Sheets

| Field | Value |
|-------|-------|
| **Sheet Name** | Earnhardt Auto Service - Oil Change Scheduler w/Upsell |
| **Document ID** | `1uI_MpilLvka7XsG0YIgpBg-hRigOGbjr9RUmmO3V0Y4` |
| **Sheet Tab** | `gid=0` (first tab) |

### Column Mappings
| Sheet Header | Source |
|--------------|-------|
| timestamp | `created_at` |
| first_name | `first_name` |
| year | `car_year` |
| car_make_model | `car_make_model` |
| phone_number | `phone_number` |
| service_type | `service_type` |
| mileage | `mileage` |
| insurance_name | `insurance_name` |
| insurance_policy_number | `insurance_policy_number` |
| claim_agent_name | `claim_agent_name` |
| claim_agent_email | `claim_agent_email` |
| claim_agent_number | `claim_agent_number` |
| upsell_interested | `upsell_interested` |
| service_summary | `service_summary` |
| qualification_score | `qualification_score` |
| call_id | `call_id` |

---

## Credentials & Config Reference

| Service | Key/ID | Notes |
|---------|--------|-------|
| Retell API Key | `key_65583dc1971057cffcc0ebe8a598` | Bearer token |
| Retell Agent ID | `agent_1366e6adc7ed1285dfe778fcee` | Dale |
| Retell LLM ID | `llm_f9dd69c5fff756372d4c89f0a6d4` | GPT-4o prompt engine |
| Retell Phone | `+17252289486` | From number for outbound |
| Service Manager Phone | `+17252491032` | route_call transfer target |
| n8n Base URL | `https://enmessara.app.n8n.cloud` | Cloud instance |
| WF1 (Post-Call) | `iEbeP2uQtxMQxlqy` | Active |
| WF Calendar Helper | `VxK2zcht3OctrDfm` | Active |
| WF2 (Outbound) | `KJk3TuaZmlqd0j9c` | Active |
| WF Utility (Watch) | `rzjOerqQJDoyNbkn` | Manual trigger |
| Google Calendar Credential | `RLxXheVb5EvaLabc` | OAuth2 |
| Google Sheets Credential | `hstzwLoRc4QOJVEG` | OAuth2 |
| Gmail Credential | `ljnLfTxRZoCe4R8Q` | OAuth2 |
| Service Manager Email | `allen@enmessara.ai` | Summary emails |
| Sales Manager Email | `allen.e89.marcus@gmail.com` | Trade-in alerts |
| Google Calendar | `allen@enmessara.ai` (primary) | Watch channel source |

---

## Slack Integration (Placeholder)
Future iteration per SLACK_INTEGRATION_INSTRUCTIONS.md pattern. Will add:
- `#earnhardt-hot-leads` channel for P0 trade-in alerts
- `#earnhardt-service-summary` for daily digests

---

## Manual Setup Required
1. **Google Sheets** - Verify column headers match mappings above
2. **Calendar Watch** - Run utility workflow to register watch channel
3. **Retell Agent** - Publish agent when ready for production calls

---

---

## Known Bugs & Fixes Applied (Testing Phase)

### Bug 1: Google Sheets Node — Missing `columns.schema` Array
**Symptom:** "Could not get parameter" error at the `Log to Google Sheets` node. All upstream nodes (webhook, filter, code, email) succeed but Sheets append fails.

**Root Cause:** When creating the Google Sheets node via API, the `columns` parameter was missing the `schema` array and `matchingColumns` array. n8n's Sheets v2 node requires these to validate column mappings at runtime.

**Fix:** Added `columns.schema` array with all 16 column definitions (each with `id`, `displayName`, `required: false`, `defaultMatch: false`, `display: true`, `type: "string"`, `canBeUsedToMatch: true`). Also added `columns.matchingColumns: []`.

**Prevention:** When creating Google Sheets nodes via API, always include the `schema` array mirroring the sheet's column headers. Copy the schema format from a working workflow.

---

### Bug 2: Google Sheets Node — Column Expressions Reference Wrong Node
**Symptom:** Column values resolve to `undefined`. The `timestamp` field shows `{{ $json.created_at }}` → undefined.

**Root Cause:** The Sheets node receives input from both Gmail nodes (Sales Manager + Service Manager). The `$json.*` expressions resolve against the Gmail node output (email metadata: id, labelIds, threadId), not the Code node output (lead_payload).

**Fix:** Changed all 16 column expressions from `$json.FIELD` to `$('Build lead_payload + Score').item.json.FIELD`. This explicitly references the Code node output regardless of which Gmail node feeds into Sheets.

**Prevention:** When a node has multiple input connections, always use explicit node references like `$('NodeName').item.json.*` instead of `$json.*`.

---

### Bug 3: Google Calendar Node v2 Not Supported on n8n Cloud
**Symptom:** Calendar workflows fail with "Install this node to use it - This node is not currently installed. It is either from a newer version of n8n, a custom node, or has an invalid structure."

**Root Cause:** The Google Calendar node was created with `typeVersion: 2`, but the n8n Cloud instance runs a version that only supports `typeVersion: 1.3`. The v2 API structure differs (e.g., `timeMin`/`timeMax` placement, `singleEvents` handling).

**Fix:** Downgraded all Google Calendar nodes from v2 to v1.3 across:
- Calendar Availability Helper workflow (`VxK2zcht3OctrDfm`)
- Outbound Call Trigger workflow (`KJk3TuaZmlqd0j9c`)

v1.3 format: `timeMin`/`timeMax` at top-level parameters (not in `options`), calendar uses `mode: "list"` with `cachedResultName`.

**Prevention:** Before creating workflows via API, check the target n8n instance's supported node versions by inspecting a working workflow's node `typeVersion`.

---

### Bug 4: Agent Language Set to en-US (Spanish STT Fails)
**Symptom:** Spanish-speaking callers not transcribed correctly.

**Root Cause:** The Retell agent `language` was set to `"en-US"` (English-only for STT). While the LLM prompt supported multi-language, the speech-to-text layer only processed English.

**Fix:** Patched agent to `language: "multi"` via Retell API.

**Prevention:** For bilingual agents, always set both the LLM language AND the agent-level language to `"multi"`.

---

## Synthetic Testing Results (Feb 14, 2026)

### Pre-Test Event Filtering
| Test | Event Type | Expected | Result |
|------|-----------|----------|--------|
| A | call_started | Filtered (no downstream) | ✅ PASS — Succeeded in 26ms |
| B | call_ended | Filtered (no downstream) | ✅ PASS — Succeeded in 23ms |
| C | call_analyzed | Full pipeline execution | ✅ PASS — After schema fix |

### Payload Validation
| Payload | Customer | Route | Expected Score | Result |
|---------|----------|-------|---------------|--------|
| Upsell=FALSE | Sarah Johnson (2024 Camry, Oil Change) | Service Manager | 10 | ✅ PASS |
| Upsell=TRUE | Carlos Rivera (2018 Civic, Tires+Upsell) | Sales Manager | 50 | ✅ PASS |

### Calendar Helper
| Test | Result |
|------|--------|
| POST /webhook/earnhardt-calendar-check | ✅ Returns 3 available slots |

---

*Built by Enmessara AI - Earnhardt Auto Shop Voice AI System*
*Last Updated: February 14, 2026*
