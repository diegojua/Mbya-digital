import subprocess
import json
import os
from datetime import datetime, timedelta, timezone

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()

def main():
    repo = os.getenv("REPO")
    app_id = os.getenv("APP_ID")
    api_key = os.getenv("API_KEY")
    phone = os.getenv("PHONE_NUMBER")
    label = os.getenv("LABEL")
    since_file = os.getenv("SINCE_FILE", "/tmp/last_gh_check")

    if not all([repo, app_id, api_key, phone]):
        print("Missing required environment variables.")
        return

    # 1. Get last check timestamp
    if os.path.exists(since_file):
        with open(since_file, "r") as f:
            last_check = f.read().strip()
    else:
        last_check = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    # 2. List issues
    # GitHub API usually expects YYYY-MM-DDTHH:MM:SSZ
    # gh search issues --repo owner/repo --created ">timestamp" --json number,title,labels
    query = f"gh search issues --repo {repo} --created \">{last_check}\" --json number,title,labels --limit 10"
    output = run_cmd(query)
    issues = json.loads(output)

    new_issues = []
    for issue in issues:
        # Filter by label if provided
        if label:
            labels = [l['name'] for l in issue['labels']]
            if label not in labels:
                continue
        new_issues.append(issue)

    # 3. Send SMS for each
    for issue in new_issues:
        msg = f"New GitHub Issue in {repo}: #{issue['number']} - {issue['title'][:100]}"
        context = {
            "app_id": app_id,
            "api_key": api_key,
            "phone_number": phone,
            "message": msg
        }
        # Run the skill
        cmd = f'hermes skill run sms-onesignal-send --context \'{json.dumps(context)}\''
        print(run_cmd(cmd))

    # 4. Update timestamp
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(since_file, "w") as f:
        f.write(now)

if __name__ == "__main__":
    main()
