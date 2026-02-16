import json
import uuid

# Load the fixed workflow (the one we just fixed auth for)
with open('earnhardt_workflow_fixed.json', 'r') as f:
    workflow = json.load(f)

# Allowed fields for PUT /workflows/:id
allowed_fields = ['name', 'nodes', 'connections', 'settings']

# 1. Update "Extract Customer Data" Code
# We need to make sure 'event_description' is returned so we can append to it later.
extract_node = next(n for n in workflow['nodes'] if n['name'] == "Extract Customer Data")
original_js = extract_node['parameters']['jsCode']
# Check if event_description is already there
if 'event_description: event.description' not in original_js:
    # Inject it into the return object
    new_js = original_js.replace(
        "    event_id: event.id",
        "    event_id: event.id,\n    event_description: description"
    )
    extract_node['parameters']['jsCode'] = new_js
    print("Updated Extract Customer Data code.")

# 2. Add "Filter: Not Already Called" Node
filter_dedup_node = {
    "parameters": {
        "conditions": {
            "options": {
                "caseSensitive": True,
                "leftValue": "",
                "typeValidation": "strict"
            },
            "conditions": [
                {
                    "id": "dedup-check",
                    "leftValue": "={{ $json.description || '' }}",
                    "rightValue": "[CALLED]",
                    "operator": {
                        "type": "string",
                        "operation": "notContains"
                    }
                }
            ],
            "combinator": "and"
        },
        "options": {}
    },
    "id": str(uuid.uuid4()),
    "name": "Filter: Not Already Called",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2,
    "position": [1232, 352] # Position between Filter Appts (1120) and Extract (1344)
}

# 3. Add "Tag Event as Called" Node
tag_event_node = {
    "parameters": {
        "method": "PATCH",
        "url": "={{ 'https://www.googleapis.com/calendar/v3/calendars/allen%40enmessara.ai/events/' + $('Extract Customer Data').item.json.event_id }}",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "googleCalendarOAuth2Api",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {
                    "name": "Content-Type",
                    "value": "application/json"
                }
            ]
        },
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ description: (($('Extract Customer Data').item.json.event_description || '') + '\\n[CALLED] ' + $now.toISO()).trim() }) }}",
        "options": {}
    },
    "id": str(uuid.uuid4()),
    "name": "Tag Event as Called",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [2000, 352], # After Retell Outbound Call (1792)
    "credentials": {
        "googleCalendarOAuth2Api": {
            "id": "RLxXheVb5EvaLabc",
            "name": "Google Calendar account"
        }
    }
}

workflow['nodes'].extend([filter_dedup_node, tag_event_node])
print("Added new nodes.")

# 4. Re-wire Connections

# Current: Filter Appointments (main 0) -> Extract Customer Data
# New: Filter Appointments (main 0) -> Filter: Not Already Called (main 0) -> Extract Customer Data

# Current: Retell Outbound Call (main 0) -> (End)
# New: Retell Outbound Call (main 0) -> Tag Event as Called

connections = workflow['connections']

# Update Filter Appointments -> Filter: Not Already Called
if "Filter Appointments" in connections:
    connections["Filter Appointments"]["main"][0][0]["node"] = "Filter: Not Already Called"

# Add Filter: Not Already Called -> Extract Customer Data
connections["Filter: Not Already Called"] = {
    "main": [
        [
            {
                "node": "Extract Customer Data",
                "type": "main",
                "index": 0
            }
        ]
    ]
}

# Add Retell Outbound Call -> Tag Event as Called
if "Retell Outbound Call" not in connections:
    connections["Retell Outbound Call"] = {"main": []}

connections["Retell Outbound Call"]["main"] = [
    [
        {
            "node": "Tag Event as Called",
            "type": "main",
            "index": 0
        }
    ]
]

print("Updated connections.")

# Clean for deployment
clean_workflow = {k: v for k, v in workflow.items() if k in allowed_fields}

# Save
with open('earnhardt_workflow_final.json', 'w') as f:
    json.dump(clean_workflow, f, indent=2)

print("Saved final workflow to earnhardt_workflow_final.json")
