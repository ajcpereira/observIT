#!/bin/bash
#observIT database import tool
#Version: 1.1

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is not installed. Please install jq and try again."
  exit 1
fi


# Define the path to the JSON config file
CONFIG_FILE="import-config.json"

# Read values from the JSON file using `jq`
INFLUX_URL=$(jq -r '.influx.url' "$CONFIG_FILE")
INFLUX_TOKEN=$(jq -r '.influx.token' "$CONFIG_FILE")
INFLUX_ORG=$(jq -r '.influx.org' "$CONFIG_FILE")
INFLUX_BUCKET=$(jq -r '.influx.bucket' "$CONFIG_FILE")
INPUT_DIR=$(jq -r '.input_dir' "$CONFIG_FILE")

# Check if the input directory exists
if [ ! -d "$INPUT_DIR" ]; then
  echo "Error: Input directory '$INPUT_DIR' does not exist. Please check your configuration."
  exit 1
fi

# Set the influx CLI configuration using the read parameters
export INFLUX_URL
export INFLUX_TOKEN
export INFLUX_ORG
export INFLUX_BUCKET

# Loop through all CSV files in the input directory and import them into InfluxDB
for CSV_FILE in "$INPUT_DIR"/*.csv; do
  if [ -f "$CSV_FILE" ]; then
    # Check if the CSV file is empty (has no data)
    if [ ! -s "$CSV_FILE" ]; then
      echo "Skipping '$CSV_FILE' as it is empty."
      continue
    fi

    # Import the CSV file into InfluxDB
    echo "Importing '$CSV_FILE' into InfluxDB bucket '$INFLUX_BUCKET'..."
    ./influx write --bucket "$INFLUX_BUCKET" --file "$CSV_FILE" --format csv
    
    if [ $? -eq 0 ]; then
      echo "Import of '$CSV_FILE' completed successfully."
    else
      echo "Error: Import of '$CSV_FILE' failed."
    fi
  else
    echo "No CSV files found in the input directory '$INPUT_DIR'."
  fi
done

echo "Import process completed."

