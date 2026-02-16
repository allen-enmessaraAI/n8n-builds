import json

# Load the fixed workflow
with open('doolittle_workflow_fixed.json', 'r') as f:
    workflow = json.load(f)

# Allowed fields for PUT /workflows/:id
# Usually: name, nodes, connections, settings, staticData, pinData, active
allowed_fields = ['name', 'nodes', 'connections', 'settings']

clean_workflow = {k: v for k, v in workflow.items() if k in allowed_fields}

# Save the clean workflow
with open('doolittle_workflow_clean.json', 'w') as f:
    json.dump(clean_workflow, f, indent=2)

print("Saved clean workflow to doolittle_workflow_clean.json")
