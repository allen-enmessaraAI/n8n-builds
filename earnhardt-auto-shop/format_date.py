import json

with open('earnhardt_workflow_final.json', 'r') as f:
    workflow = json.load(f)

allowed_fields = ['name', 'nodes', 'connections', 'settings']

# Find Extract Customer Data node
extract_node = next(n for n in workflow['nodes'] if n['name'] == "Extract Customer Data")

# New JavaScript code with natural date formatting
new_js = r"""const event = $input.item.json;
const title = event.summary || '';
const description = event.description || '';

// Parse: "Service | Customer Name | Service Type"
const parts = title.split('|').map(s => s.trim());
const customer_name = parts[1] || 'valued customer';
const appointment_type = parts[2] || 'auto service';
const raw_time = event.start?.dateTime || event.start?.date || '';

// Format date naturally for voice agent (e.g. "February 17th")
let appointment_time = raw_time;
if (raw_time) {
  const d = new Date(raw_time);
  const months = ['January','February','March','April','May','June',
                   'July','August','September','October','November','December'];
  const day = d.getDate();
  const suffix = (day === 1 || day === 21 || day === 31) ? 'st'
               : (day === 2 || day === 22) ? 'nd'
               : (day === 3 || day === 23) ? 'rd' : 'th';
  appointment_time = months[d.getMonth()] + ' ' + day + suffix;
}

// Extract phone from description
const phoneRegex = /(Phone|phone_number|phone)\s*:\s*([+\d\-\s()]+)/i;
const phoneMatch = description.match(phoneRegex);
let phone_raw = phoneMatch ? phoneMatch[2] : '';

// Normalize to E.164
let phone_normalized = '';
if (phone_raw) {
  const digitsOnly = phone_raw.replace(/\D/g, '');
  if (digitsOnly.length === 10) phone_normalized = `+1${digitsOnly}`;
  else if (digitsOnly.length === 11 && digitsOnly[0] === '1') phone_normalized = `+${digitsOnly}`;
  else if (digitsOnly.length > 11) phone_normalized = `+${digitsOnly}`;
}

return {
  json: {
    customer_name,
    appointment_time,
    appointment_type,
    phone_number: phone_normalized,
    event_id: event.id,
    event_description: description
  }
};"""

extract_node['parameters']['jsCode'] = new_js
print("Updated Extract Customer Data with natural date formatting.")

# Clean and save
clean_workflow = {k: v for k, v in workflow.items() if k in allowed_fields}
with open('earnhardt_workflow_final.json', 'w') as f:
    json.dump(clean_workflow, f, indent=2)

print("Saved updated workflow to earnhardt_workflow_final.json")
