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

def monitor():
    # Load config from env
    repo = os.environ.get("REPO", "public-apis/public-apis")
    app_id = os.environ.get("ONE_SIGNAL_APP_ID")
    api_key = os.environ.get("ONE_SIGNAL_API_KEY")
    phone_number = os.environ.get("PHONE_NUMBER")
    label = os.environ.get("LABEL")
    since_file = os.environ.get("SINCE_FILE", "/tmp/last_gh_check")
    
    if not (app_id and api_key and phone_number):
        print("Missing required environment variables")
        return

    since = get_last_check(since_file)
    
    # List issues
    search_query = f"repo:{repo} is:issue created:>{since}"
    cmd = ["gh", "api", "search/issues", "-f", f"q={search_query}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error listing issues: {result.stderr}")
        return
        
    data = json.loads(result.stdout)
    items = data.get('items', [])
    
    new_issues = []
    for issue in items:
        # Filter by label if requested
        if label:
            labels = [l['name'] for l in issue.get('labels', [])]
            if label not in labels:
                continue
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
        # Run the official skill
        subprocess.run(["hermes", "skill", "run", "sms-onesignal-send", "--context", json.dumps(context)])
        
    with open(since_file, 'w') as f:
        f.write(datetime.now().isoformat())

if __name__ == "__main__":
    monitor()
