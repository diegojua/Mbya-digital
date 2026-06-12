import subprocess
import json
import os
import sys
from datetime import datetime, timedelta

def get_last_check(since_file):
    if os.path.exists(since_file):
        with open(since_file, 'r') as f:
            return f.read().strip()
    return (datetime.now() - timedelta(hours=1)).isoformat()

def update_last_check(since_file):
    with open(since_file, 'w') as f:
        f.write(datetime.now().isoformat())

def monitor(repo, app_id, api_key, phone_number, label=None, since_file='/tmp/last_gh_check'):
    since = get_last_check(since_file)
    
    # List issues since timestamp
    cmd = ["gh", "issue", "list", "-R", repo, "--json", "number,title,createdAt,labels", "--state", "open"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error listing issues: {result.stderr}")
        return
        
    issues = json.loads(result.stdout)
    new_issues = []
    for issue in issues:
        if issue['createdAt'] > since:
            if label:
                if any(l['name'] == label for l in issue['labels']):
                    new_issues.append(issue)
            else:
                new_issues.append(issue)
                
    if not new_issues:
        print("[SILENT]")
        return
        
    for issue in new_issues:
        msg = f"New issue in {repo}: #{issue['number']} - {issue['title']}"
        context = {
            "app_id": app_id,
            "api_key": api_key,
            "phone_number": phone_number,
            "message": msg
        }
        subprocess.run(["hermes", "skill", "run", "sms-onesignal-send", "--context", json.dumps(context)])
        
    update_last_check(since_file)

if __name__ == "__main__":
    # Expecting args or config, but since this is a cron job, hardcoding or env is expected
    # The prompt asked for config via context.
    # I will simulate the context by checking env vars if provided, or defaults.
    repo = os.environ.get("REPO", "public-apis/public-apis")
    app_id = os.environ.get("ONE_SIGNAL_APP_ID")
    api_key = os.environ.get("ONE_SIGNAL_API_KEY")
    phone = os.environ.get("PHONE_NUMBER")
    label = os.environ.get("LABEL")
    
    if not (app_id and api_key and phone):
        print("Missing required environment variables for SMS")
        sys.exit(1)
        
    monitor(repo, app_id, api_key, phone, label)
