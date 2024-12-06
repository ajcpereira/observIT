#!/bin/bash
#observIT database export tool
#Version: 1.1

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is not installed. Please install jq and try again."
  exit 1
fi

# Define the path to the JSON config file
CONFIG_FILE="export-config.json"

# Read values from the JSON file using `jq`
START_TIME=$(jq -r '.start_time' "$CONFIG_FILE")
STOP_TIME=$(jq -r '.stop_time' "$CONFIG_FILE")
OUTPUT_DIR=$(jq -r '.output_dir' "$CONFIG_FILE")
#INFLUX_URL=$(jq -r '.influx.url' "$CONFIG_FILE")
#INFLUX_TOKEN=$(jq -r '.influx.token' "$CONFIG_FILE")
INFLUX_ORG=$(jq -r '.influx.org' "$CONFIG_FILE")
INFLUX_BUCKET=$(jq -r '.influx.bucket' "$CONFIG_FILE")
MEASUREMENTS=$(jq -r '.measurements[]' "$CONFIG_FILE")

# Create the output directory if it doesn't exist
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Set the influx CLI configuration using the read parameters
#export INFLUX_URL
#export INFLUX_TOKEN
export INFLUX_ORG
export INFLUX_BUCKET

# Loop through each measurement and create a Flux query, write to query.flux, and execute the command
for MEASUREMENT in ${MEASUREMENTS}; do
  # Create the Flux query for the current measurement
  QUERY="from(bucket: \"$INFLUX_BUCKET\")
    |> range(start: $START_TIME, stop: $STOP_TIME)
    |> filter(fn: (r) => r[\"_measurement\"] == \"$MEASUREMENT\")
    |> drop(columns: [\"_start\", \"_stop\"])"

  # Write the current query to query.flux
  echo "$QUERY" > query.flux
  
  # Execute the influx command and redirect output to an export file named after the measurement
  ./influx query --skip-verify --raw --file ./query.flux > "$OUTPUT_DIR/export_${MEASUREMENT}.csv"
  
  echo "Query for measurement '$MEASUREMENT' complete. Results saved to $OUTPUT_DIR/export_${MEASUREMENT}.csv"
done

# Compress and tar the folder with all the results
TAR_FILE="export_$(date +%Y-%m-%d).tar.gz"
tar -czf "$TAR_FILE" "$OUTPUT_DIR"

echo "Results folder '$OUTPUT_DIR' has been compressed into '$TAR_FILE'."


