#!/usr/bin/env bash

# Replace the cron schedule placeholder with the actual SCHEDULE environment variable
CRON_COMMAND="DRY_RUN=${DRY_RUN:-"false"}"
CRON_COMMAND+=" INPUT_FOLDER=${INPUT_FOLDER}"
CRON_COMMAND+=" OUTPUT_FOLDER=${OUTPUT_FOLDER}"
CRON_COMMAND+=" OUTPUT_USER=${OUTPUT_USER:-"root"}"
CRON_COMMAND+=" OUTPUT_GROUP=${OUTPUT_GROUP:-"root"}"
CRON_COMMAND+=" KEEP_N_DAYS=${KEEP_N_DAYS:-"0"}"
CRON_COMMAND+=" KEEP_N_FILES=${KEEP_N_FILES:-"0"}"
CRON_COMMAND+=" /usr/local/bin/python /app/main.py"

echo "------------------------------------------------------------------"
echo "Starting backup cron job - $(date)"
echo "Schedule: ${SCHEDULE}"
echo "Input folder: ${INPUT_FOLDER}"
echo "Output folder: ${OUTPUT_FOLDER}"
echo "User: ${OUTPUT_USER:-"root"}"
echo "Group: ${OUTPUT_GROUP:-"root"}"
echo "Installing Cron:"
echo "${SCHEDULE} ${CRON_COMMAND}>> /var/log/cron.log 2>&1"
echo "------------------------------------------------------------------"
echo "${SCHEDULE} ${CRON_COMMAND}>> /var/log/cron.log 2>&1" > /etc/cron.d/scheduled-job

# Give execution rights on the cron job
chmod 0644 /etc/cron.d/scheduled-job

# Apply the cron job
crontab /etc/cron.d/scheduled-job

# Create the log file to be able to run tail
touch /var/log/cron.log

# Define the cleanup function
cleanup() {
    echo "Cleaning up..."

    pkill cron

    echo "Cleanup complete."
}

# Set trap for INT (Ctrl+C) and EXIT
trap cleanup INT EXIT

# Start the cron daemon and display logs
cron -f &
echo "Running Initial Backup..."
eval "${CRON_COMMAND}" >> /var/log/cron.log 2>&1
tail -f /var/log/cron.log
