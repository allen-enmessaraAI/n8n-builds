import json

# Load the original workflow
with open('workflow.json', 'r') as f:
    workflow = json.load(f)

# Define correct constants for Earnhardt
EARNHARDT_AGENT_ID = "agent_1366e6adc7ed1285dfe778fcee"
EARNHARDT_PHONE = "+17252289486"
EARNHARDT_API_KEY = "key_65583dc1971057cffcc0ebe8a598"

# Allowed fields for PUT /workflows/:id
allowed_fields = ['name', 'nodes', 'connections', 'settings']

target_node_name = "Retell Outbound Call"
node_found = False

for node in workflow['nodes']:
    if node['name'] == target_node_name:
        node_found = True
        print(f"Found node: {target_node_name}")
        
        # 1. REMOVE Custom Auth
        if 'credentials' in node:
            del node['credentials']
        node['parameters']['authentication'] = 'genericCredentialType'
        node['parameters']['genericAuthType'] = 'httpHeaderAuth' # Start with this but we will actually just use manual headers if possible or just Header Auth
        # Actually simplest is 'authentication': 'none' and send headers manually
        node['parameters']['authentication'] = 'none' # No credential reference
        
        # 2. ADD Manual Headers
        # Note: 'headerParameters' structure is { parameters: [ {name, value}, ... ] }
        node['parameters']['sendHeaders'] = True
        node['parameters']['headerParameters'] = {
            "parameters": [
                {
                    "name": "Authorization",
                    "value": f"Bearer {EARNHARDT_API_KEY}"
                },
                {
                    "name": "Content-Type",
                    "value": "application/json"
                }
            ]
        }
        
        # 3. FIX JSON Body
        # Must use valid n8n expression syntax: ={{ JSON.stringify(...) }}
        # We construct the JS object string carefully
        
        js_expression = """={{ JSON.stringify({
  "from_number": "%s",
  "to_number": $json.phone_number,
  "override_agent_id": "%s",
  "retell_llm_dynamic_variables": {
    "customer_name": $json.customer_name,
    "appointment_time": $json.appointment_time,
    "appointment_type": $json.appointment_type
  }
}) }}""" % (EARNHARDT_PHONE, EARNHARDT_AGENT_ID)

        node['parameters']['sendBody'] = True
        node['parameters']['specifyBody'] = 'json'
        node['parameters']['jsonBody'] = js_expression
        
        print("Updated Auth and JSON Body.")
        break

if not node_found:
    print(f"Error: Node '{target_node_name}' not found.")
    exit(1)

# Clean the workflow for deployment
clean_workflow = {k: v for k, v in workflow.items() if k in allowed_fields}

# Save the fixed workflow
with open('earnhardt_workflow_fixed.json', 'w') as f:
    json.dump(clean_workflow, f, indent=2)

print("Saved fixed workflow to earnhardt_workflow_fixed.json")
