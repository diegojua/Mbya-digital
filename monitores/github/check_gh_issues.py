import subprocess
import json
import os
import datetime

# Configuration from env or defaults
REPO = os.environ.get("GITHUB_REPO")
APP_ID = os.environ.get("ONE_SIGNAL_APP_ID")
API_KEY = os.environ.get("ONE_SIGNAL_API_KEY")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER")
SINCE_FILE = "/tmp/last_gh_check"
LABEL = os.environ.get("ISSUE_LABEL")

if not REPO or not APP_ID or not API_KEY or not PHONE_NUMBER:
    print("Missing required configuration environment variables.")
    exit(1)

# 1. Get last check time
if os.path.exists(SINCE_FILE):
    with open(SINCE_FILE, "r") as f:
        since = f.read().strip()
else:
    since = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat()

# 2. Get new issues
# Using gh cli to fetch issues since timestamp
# --json title,url,createdAt,labels
cmd = ["gh", "issue", "list", "-R", REPO, "--since", since, "--json", "title,url,createdAt,labels", "--limit", "10"]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"Error fetching issues: {result.stderr}")
    exit(1)

issues = json.loads(result.stdout)
new_issues = []
for issue in issues:
    # filter by label if provided
    if LABEL:
        labels = [l['name'] for l in issue['labels']]
        if LABEL not in labels:
            continue
    new_issues.append(issue)

# 3. Send SMS for each
if not new_issues:
    print("[SILENT]")
    # Update timestamp anyway to avoid re-checking old issues
    with open(SINCE_FILE, "w") as f:
        f.write(datetime.datetime.now().isoformat())
    exit(0)

for issue in new_issues:
    msg = f"New issue in {REPO}: {issue['title']} {issue['url']}"
    context = {
        "app_id": APP_ID,
        "api_key": API_KEY,
        "phone_number": PHONE_NUMBER,
        "message": msg
    }
    # Call the skill
    subprocess.run(["hermes", "skill", "run", "sms-onesignal-send", "--context", json.dumps(context)])

# 4. Update timestamp
with open(SINCE_FILE, "w") as f:
    f.write(datetime.datetime.now().isoformat())

print(f"Processed {len(new_issues)} new issues.")
