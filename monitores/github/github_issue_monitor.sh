#!/bin/bash
# GitHub Issue Monitor and SMS Notifier

REPO="public-apis/public-apis"
SINCE_FILE="/tmp/last_gh_check"
LABEL="bug"

# Credentials should be fetched from environment if present
APP_ID="${ONE_SIGNAL_APP_ID}"
API_KEY="${ONE_SIGNAL_API_KEY}"
PHONE_NUMBER="${DESTINATION_PHONE_NUMBER}"

if [ -z "$APP_ID" ] || [ -z "$API_KEY" ] || [ -z "$PHONE_NUMBER" ]; then
    echo "Missing required environment variables (ONE_SIGNAL_APP_ID, ONE_SIGNAL_API_KEY, DESTINATION_PHONE_NUMBER)"
    exit 1
fi

# 1. Get last check time
if [ -f "$SINCE_FILE" ]; then
    LAST_CHECK=$(cat "$SINCE_FILE")
else
    LAST_CHECK=$(date -u -d "1 hour ago" +"%Y-%m-%dT%H:%M:%SZ")
fi

# 2. List new issues
NEW_ISSUES=$(gh issue list --repo "$REPO" --limit 20 --json number,title,createdAt | jq -c ".[] | select(.createdAt > \"$LAST_CHECK\")")

# 3. Process new issues
if [ -z "$NEW_ISSUES" ]; then
    exit 0 # Silent exit
fi

while read -r issue; do
    TITLE=$(echo "$issue" | jq -r .title)
    NUMBER=$(echo "$issue" | jq -r .number)
    
    MESSAGE="New GitHub Issue in $REPO: #$NUMBER - $TITLE"
    
    # Send via OneSignal skill
    hermes -z "Use the sms-onesignal-send skill with app_id='$APP_ID', api_key='$API_KEY', phone_number='$PHONE_NUMBER', message='$MESSAGE'"
done <<< "$NEW_ISSUES"

# 4. Update timestamp
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$SINCE_FILE"
