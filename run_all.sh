#!/bin/bash

# BARN Challenge Runner Script - Official Guideline Compliant
# This script iterates through all BARN and DynaBARN worlds.
# It uses the official launch file without any physics modifications.

# Define range of worlds
# Static: 0-299, Dynamic: 300-359
START_WORLD=0
END_WORLD=359

for i in $(seq $START_WORLD $END_WORLD); do
    echo "=========================================="
    echo "Launching BARN Challenge World Index: $i"
    echo "=========================================="
    
    # Run the official launch file
    # gui:=false ensures headless mode to maximize RTF on your hardware
    # world_idx:=$i passes the specific environment index to the runner
    
    ros2 launch jackal_helper BARN_runner.launch.py \
        gui:=false \
        world_idx:=$i \
        out_file:="results_world_$i.txt"
    
    echo "Trial for world $i completed."
    
    # Optional: Brief pause between trials to allow resources to clear
    sleep 2
done

echo "All trials completed."
