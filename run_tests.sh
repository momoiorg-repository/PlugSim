#!/bin/bash
# run_tests.sh — run PlugSim unit tests (excludes ROS Python 3.12 paths)

CLEAN_PYTHONPATH=""
IFS=':' read -ra PARTS <<< "${PYTHONPATH:-}"
for part in "${PARTS[@]}"; do
    [[ "$part" != *"/opt/ros/"* ]] && \
        CLEAN_PYTHONPATH="${CLEAN_PYTHONPATH}${CLEAN_PYTHONPATH:+:}${part}"
done
CLEAN_PYTHONPATH="$(pwd):${CLEAN_PYTHONPATH}"

echo "Running PlugSim tests..."
PYTHONPATH="$CLEAN_PYTHONPATH" python -m pytest tests/ "$@"
