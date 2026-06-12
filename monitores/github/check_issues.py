import subprocess
import json
import os
import datetime

# Config
REPO = os.getenv('GITHUB_REPO')
APP_ID = os.getenv('ONE_SIGNAL_APP_ID')
API_KEY = os.getenv('ONE_SIGNAL_API_KEY')
PHONE = os.getenv('PHONE_NUMBER')
LABEL = os.getenv('ISSUE_LABEL')
SINCE_FILE = '/tmp/last_gh_check'

def get_last_check():
    if os.path.exists(SINCE_FILE):
        with open(SINCE_FILE, 'r') as f:
            return datetime.datetime.fromisoformat(f.read().strip())
    return datetime.datetime.now() - datetime.timedelta(hours=1)

def update_last_check():
    with open(SINCE_FILE, 'w') as f:
        f.write(datetime.datetime.now().isoformat())

def send_sms(message):
    # Call the skill directly as requested
    cmd = [
        "hermes", "skill", "run", "sms-onesignal-send",
        "--context", json.dumps({
            "app_id": APP_ID,
            "api_key": API_KEY,
            "phone_number": PHONE,
            "message": message
        })
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    return True

def main():
    last_check = get_last_check()
    
    # List issues using gh CLI
    # Use -R for repo instead of search in current folder
    query = f"is:issue is:open created:>{last_check.isoformat()}Z"
    if LABEL:
        query += f" label:{LABEL}"
        
    cmd = ["gh", "issue", "list", "-R", REPO, "--search", query, "--json", "title,number,labels"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return

    issues = json.loads(result.stdout)
            
    if not issues:
        print("[SILENT]")
        return
        
    for issue in issues:
        msg = f"New GitHub issue in {REPO}: #{issue['number']} - {issue['title']}"
        send_sms(msg)
        
    update_last_check()

if __name__ == "__main__":
    main()
