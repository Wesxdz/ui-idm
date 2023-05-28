#!/bin/bash

# Check if OBS is already running
if pgrep -x "obs" > /dev/null; then
    echo "OBS is already running."
else
    # Launch OBS
    echo "Starting OBS..."
    obs &
fi

# Activate Conda environment and run Python script
echo "Activating Conda environment..."
conda activate booksim

# Run Python script
echo "Running idm.py..."
python idm.py
