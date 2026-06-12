import subprocess
import json
import os
import datetime
import requests
import sys

def get_last_check(since_file):
    if os.path.exists(since_file):
        with open(since_file, 'r') as f:
            return f.read().strip()
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)).isoformat()

def update_last_check(since_file):
    with open(since_file, 'w') as f:
        f.write(datetime.datetime.now(datetime.timezone.utc).isoformat())

def get_new_issues(repo, since, label=None):
    # Constructing query: repo:owner/repo created:>timestamp
    query = f"repo:{repo} is:issue created:>{since}"
    if label:
        query += f" label:{label}"
    
    cmd = ["gh", "search", "issues", "--json", "number,title,url", "--limit", "10", query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return json.loads(result.stdout)

def send_sms(app_id, api_key, phone_number, message):
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Authorization": f"Basic {api_key}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "app_id": app_id,
        "contents": {"en": message},
        "include_phone_numbers": [phone_number]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def main():
    # Context expected from env or hardcoded logic for cron
    # Since this is a cron, we assume these are passed or defined
    repo = os.getenv("GITHUB_REPO")
    app_id = os.getenv("ONESIGNAL_APP_ID")
    api_key = os.getenv("ONESIGNAL_API_KEY")
    phone_number = os.getenv("PHONE_NUMBER")
    label = os.getenv("ISSUE_LABEL")
    since_file = os.getenv("SINCE_FILE", "/tmp/last_gh_check")

    if not all([repo, app_id, api_key, phone_number]):
        print("Missing required configuration")
        sys.exit(1)

    since = get_last_check(since_file)
    issues = get_new_issues(repo, since, label)
    
    if not issues:
        print("[SILENT]")
        return

    for issue in issues:
        message = f"New issue in {repo}: #{issue['number']} - {issue['title']}"
        send_sms(app_id, api_key, phone_number, message)
    
    update_last_check(since_file)
    print(f"Processed {len(issues)} new issues.")

if __name__ == "__main__":
    main()
