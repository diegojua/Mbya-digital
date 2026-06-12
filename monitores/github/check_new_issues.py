import subprocess
import json
import os
from datetime import datetime

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip()

repo = os.environ.get("REPO", "public-apis/public-apis")
since_file = "/tmp/last_gh_check"
if os.path.exists(since_file):
    with open(since_file, "r") as f:
        since = f.read().strip()
else:
    since = "2026-06-03T00:00:00Z"

# List issues
cmd = f'gh search issues --repo {repo} --created ">{since}" --json number,title,url'
output = run_cmd(cmd)
if not output:
    print("[SILENT]")
    exit()

issues = json.loads(output)
if not issues:
    print("[SILENT]")
else:
    for issue in issues:
        print(f"Found issue: {issue['number']} - {issue['title']}")

# Update timestamp
with open(since_file, "w") as f:
    f.write(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
