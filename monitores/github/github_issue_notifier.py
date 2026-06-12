import json
import subprocess
import os
import datetime
import requests
import sys

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"Error executing command: {cmd}\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def send_sms(context, message):
    # This calls the sms-onesignal-send skill internally via CLI
    ctx = {
        "app_id": context['app_id'],
        "api_key": context['api_key'],
        "phone_number": context['phone_number'],
        "message": message
    }
    cmd = f"hermes skill run sms-onesignal-send --context '{json.dumps(ctx)}'"
    return run_cmd(cmd)

def main():
    # Load config from environment or defaults - since this is a cron, expect it passed via env
    repo = os.environ.get("GITHUB_REPO")
    app_id = os.environ.get("ONESIGNAL_APP_ID")
    api_key = os.environ.get("ONESIGNAL_API_KEY")
    phone_number = os.environ.get("PHONE_NUMBER")
    label = os.environ.get("ISSUE_LABEL")
    since_file = os.environ.get("SINCE_FILE", "/tmp/last_gh_check")

    if not all([repo, app_id, api_key, phone_number]):
        print("Missing required environment variables.")
        sys.exit(1)

    # 1. Get timestamp
    if os.path.exists(since_file):
        with open(since_file, "r") as f:
            last_check = f.read().strip()
    else:
        last_check = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat()

    # 2. Query GitHub for issues
    # gh doesn't support --since directly on issue list, use search query
    cmd = f"gh issue list -R {repo} -s open --json number,title,labels,createdAt"
    output = run_cmd(cmd)
    all_issues = json.loads(output)
    issues = [i for i in all_issues if i['createdAt'] > last_check]

    new_issues = []
    for issue in issues:
        # Check label filter
        if label:
            labels = [l['name'] for l in issue['labels']]
            if label not in labels:
                continue
        new_issues.append(issue)

    # 3. Send alerts
    if not new_issues:
        print("[SILENT]")
        return

    context = {"app_id": app_id, "api_key": api_key, "phone_number": phone_number}
    for issue in new_issues:
        msg = f"New issue in {repo}: #{issue['number']} - {issue['title']}"
        send_sms(context, msg)

    # 4. Update timestamp
    with open(since_file, "w") as f:
        f.write(datetime.datetime.now().isoformat())

if __name__ == "__main__":
    main()
