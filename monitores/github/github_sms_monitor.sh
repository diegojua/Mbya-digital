#!/bin/bash

# Configuration
REPO=$1
APP_ID=$2
API_KEY=$3
PHONE_NUMBER=$4
LABEL=$5
SINCE_FILE=${6:-/tmp/last_gh_check}

# 1. Read last check timestamp
if [ -f "$SINCE_FILE" ]; then
    SINCE=$(cat "$SINCE_FILE")
else
    # Default to 1 hour ago
    SINCE=$(date -d "1 hour ago" -u +"%Y-%m-%dT%H:%M:%SZ")
fi

# 2. Use gh CLI to list issues created since that timestamp
# Filter by label if provided
GH_QUERY="repo:$REPO is:issue created:>$SINCE"
if [ -n "$LABEL" ]; then
    GH_QUERY="$GH_QUERY label:$LABEL"
fi

ISSUES=$(gh issue list --search "$GH_QUERY" --json number,title,url --limit 10)

# 3. Process new issues
# Check if issues found (gh returns [] if none)
if [ "$ISSUES" != "[]" ]; then
    echo "$ISSUES" | jq -c '.[]' | while read -r issue; do
        TITLE=$(echo "$issue" | jq -r '.title')
        URL=$(echo "$issue" | jq -r '.url')
        MESSAGE="New GitHub Issue in $REPO: $TITLE. See: $URL"
        
        # Send SMS via OneSignal skill
        hermes skill run sms-onesignal-send \
          --context "{\"app_id\": \"$APP_ID\", \"api_key\": \"$API_KEY\", \"phone_number\": \"$PHONE_NUMBER\", \"message\": \"$MESSAGE\"}"
    done
fi

# 4. Update since_file with current timestamp
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$SINCE_FILE"
