#!/bin/bash
export GH_REPO=$(jq -r '.repo' /home/diego/.hermes/config/gh_onesignal.json)
export ONESIGNAL_APP_ID=$(jq -r '.app_id' /home/diego/.hermes/config/gh_onesignal.json)
export ONESIGNAL_API_KEY=$(jq -r '.api_key' /home/diego/.hermes/config/gh_onesignal.json)
export TARGET_PHONE=$(jq -r '.phone_number' /home/diego/.hermes/config/gh_onesignal.json)
export GH_LABEL=$(jq -r '.label' /home/diego/.hermes/config/gh_onesignal.json)
export SINCE_FILE=$(jq -r '.since_file' /home/diego/.hermes/config/gh_onesignal.json)

python3 /home/diego/.hermes/hermes-agent/scripts/gh_to_sms.py
