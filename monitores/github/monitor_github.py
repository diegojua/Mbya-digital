import json
import subprocess
import os
from datetime import datetime, timedelta

# Config (read from json)
with open('/home/diego/github_monitor.json', 'r') as f:
    config = json.load(f)

repo = config['repo']
app_id = config['app_id']
api_key = config['api_key']
phone = config['phone_number']
label = config.get('label')
since_file = config.get('since_file', '/tmp/last_gh_check')

# Get last check
if os.path.exists(since_file):
    with open(since_file, 'r') as f:
        since = f.read().strip()
else:
    since = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"

now = datetime.utcnow().isoformat() + "Z"

# List issues
cmd = ["gh", "issue", "list", "-R", repo, "-S", f"created:>={since}", "--json", "number,title,labels"]
result = subprocess.run(cmd, capture_output=True, text=True)
issues = json.loads(result.stdout)

filtered = []
if label:
    for issue in issues:
        if any(l['name'] == label for l in issue['labels']):
            filtered.append(issue)
else:
    filtered = issues

if not filtered:
    print("[SILENT]")
    exit()

# Send SMS
for issue in filtered:
    msg = f"New GitHub Issue #{issue['number']}: {issue['title']}"
    context = {
        "app_id": app_id,
        "api_key": api_key,
        "phone_number": phone,
        "message": msg
    }
    # Call the skill
    # Since I'm in the agent environment, I can use the tool directly
    # Wait, I don't have a direct 'call skill' tool, I have 'terminal'
    # Use 'hermes skill run'
    subprocess.run(["hermes", "skill", "run", "sms-onesignal-send", "--context", json.dumps(context)])

# Update timestamp
with open(since_file, 'w') as f:
    f.write(now)
