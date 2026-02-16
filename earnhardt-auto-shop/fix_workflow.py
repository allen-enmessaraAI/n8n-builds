import json

# Load the workflow
with open('doolittle_workflow.json', 'r') as f:
    workflow = json.load(f)

# Find the target node
target_node_name = "Filter: Appointment Events"
node_found = False

for node in workflow['nodes']:
    if node['name'] == target_node_name:
        node_found = True
        print(f"Found node: {target_node_name}")
        
        # Add the exclusion condition
        # Logic: Summary must NOT contain "Service"
        new_condition = {
            "id": "filter-not-service",
            "leftValue": "={{ $json.summary }}",
            "rightValue": "Service",
            "operator": {
                "type": "string",
                "operation": "notContains"
            }
        }
        
        # Ensure 'conditions' list exists (it matches existing structure)
        conditions_list = node['parameters']['conditions']['conditions']
        conditions_list.append(new_condition)
        print("Added 'notContains' condition for 'Service'.")
        break

if not node_found:
    print(f"Error: Node '{target_node_name}' not found.")
    exit(1)

# Save the fixed workflow
with open('doolittle_workflow_fixed.json', 'w') as f:
    json.dump(workflow, f, indent=2)

print("Saved fixed workflow to doolittle_workflow_fixed.json")
