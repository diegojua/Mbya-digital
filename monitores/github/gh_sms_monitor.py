import os
import json
import subprocess
import datetime

def run():
    repo = os.getenv("GITHUB_REPO")
    app_id = os.getenv("ONESIGNAL_APP_ID")
    api_key = os.getenv("ONESIGNAL_API_KEY")
    phone = os.getenv("PHONE_NUMBER")
    since_file = os.getenv("SINCE_FILE", "/tmp/last_gh_check")
    label = os.getenv("ISSUE_LABEL")

    if not all([repo, app_id, api_key, phone]):
        # If no config provided, nothing to do.
        print("[SILENT]")
        return

    if os.path.exists(since_file):
        with open(since_file, "r") as f:
            last_check = f.read().strip()
    else:
        last_check = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Search query for GH
    search_query = f"repo:{repo} is:issue is:open created:>{last_check}"
    if label:
        search_query += f" label:{label}"

    result = subprocess.run(["gh", "search", "issues", search_query, "--json", "number,title,labels"], capture_output=True, text=True)
    
    if result.returncode != 0:
        return

    try:
        issues = json.loads(result.stdout)
    except:
        issues = []

    if not issues:
        print("[SILENT]")
        return

    # Trigger skill via CLI (as per instruction)
    for issue in issues:
        msg = f"New GitHub Issue in {repo}: {issue['title']} (#{issue['number']})"
        ctx = json.dumps({
            "app_id": app_id, 
            "api_key": api_key, 
            "phone_number": phone, 
            "message": msg
        })
        subprocess.run(["hermes", "skill", "run", "sms-onesignal-send", "--context", ctx])

    with open(since_file, "w") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

run()
