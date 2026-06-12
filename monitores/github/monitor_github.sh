#!/bin/bash
REPO="public-apis/public-apis"
SINCE_FILE="/tmp/last_gh_check"
LABEL="bug"

# Read last check time
if [ -f "$SINCE_FILE" ]; then
    SINCE=$(cat "$SINCE_FILE")
else
    # Default to 1 hour ago
    SINCE=$(date -d "1 hour ago" -u +"%Y-%m-%dT%H:%M:%SZ")
fi

# List new issues
ISSUES=$(gh issue list -R "$REPO" -L 10 --json number,title,createdAt -q ".[] | select(.createdAt > \"$SINCE\") | select(.labels[].name == \"$LABEL\")")

# Update since_file
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$SINCE_FILE"

if [ -z "$ISSUES" ]; then
    exit 0
fi

# For each issue, send SMS
echo "$ISSUES" | jq -c '.[]' | while read -r issue; do
    TITLE=$(echo "$issue" | jq -r '.title')
    NUMBER=$(echo "$issue" | jq -r '.number')
    MSG="New Issue #$NUMBER in $REPO: $TITLE"
    
    hermes skill run sms-onesignal-send \
        --context "{\"app_id\": \"$ONE_SIGNAL_APP_ID\", \"api_key\": \"$ONE_SIGNAL_API_KEY\", \"phone_number\": \"+155****9999\", \"message\": \"$MSG\"}"
done
