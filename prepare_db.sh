#!/bin/bash

# Check if a date argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 yyyy-mm-dd"
  exit 1
fi

INPUT_DATE="$1"

# Validate format (basic check)
if [[ ! "$INPUT_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "Error: Date must be in yyyy-mm-dd format"
  exit 1
fi

# Convert to yyyymmdd
FORMATTED_DATE=$(echo "$INPUT_DATE" | tr -d '-')

# Retrieve the telemetry
tmpy -s 10258 -b 2026-01-01T00:00:00Z -e ${INPUT_DATE}T00:00:00Z
tmpy -s 10265 -b 2026-01-01T00:00:00Z -e ${INPUT_DATE}T00:00:00Z
tmpy -s 10428 -b 2026-01-01T00:00:00Z -e ${INPUT_DATE}T00:00:00Z

# Prepare the sandbox
rm -rf sandbox
mkdir sandbox

# Generate the sandbox content

python ssmm_juice_tm.py -f tm_10258_20260101T000000Z_${FORMATTED_DATE}T000000Z.dds -o sandbox -s
python ssmm_juice_tm.py -f tm_10265_20260101T000000Z_${FORMATTED_DATE}T000000Z.dds -o sandbox -s
python ssmm_juice_tm.py -f tm_10428_20260101T000000Z_${FORMATTED_DATE}T000000Z.dds -o sandbox -s

# Recreate the database
python flask_snapshots/ingest_json.py --data_dir sandbox --db_path flask_snapshots/snapshots.db 