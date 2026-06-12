import json
import subprocess
import requests
import datetime
import os

def load_config():
    with open('/home/diego/github_monitor.json', 'r') as f:
        return json.load(f)

def get_last_check(since_file):
    if os.path.exists(since_file):
        with open(since_file, 'r') as f:
            return f.read().strip()
    else:
        # Default to 1 hour ago
        time_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
        return time_ago.isoformat()

def save_last_check(since_file, timestamp):
    with open(since_file, 'w') as f:
        f.write(timestamp)

def fetch_issues(repo, since, label=None):
    cmd = ["gh", "issue", "list", "-R", repo, "--state", "open", "--json", "number,title,createdAt,labels", "--limit", "50"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    
    issues = json.loads(result.stdout)
    new_issues = []
    for issue in issues:
        if issue['createdAt'] > since:
            if label:
                if any(l['name'] == label for l in issue['labels']):
                    new_issues.append(issue)
            else:
                new_issues.append(issue)
    return new_issues

def send_sms(config, message):
    payload = {
        "app_id": config['app_id'],
        "api_key": config['api_key'],
        "phone_number": config['phone_number'],
        "message": message
    }
    # Using internal call simulate via shell for now or just printing for test
    print(f"Would send: {message}")

config = load_config()
last_check = get_last_check(config['since_file'])
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

new_issues = fetch_issues(config['repo'], last_check, config.get('label'))

if new_issues:
    for issue in new_issues:
        msg = f"New issue in {config['repo']}: {issue['title']} (#{issue['number']})"
        print(f"Sending SMS: {msg}")
        subprocess.run(['hermes', 'skill', 'run', 'sms-onesignal-send', '--context', json.dumps({
            "app_id": config['app_id'],
            "api_key": config['api_key'],
            "phone_number": config['phone_number'],
            "message": msg
        })])

save_last_check(config['since_file'], now)