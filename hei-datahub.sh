#!/usr/bin/env bash
#
# Convenience script to run hei-datahub from anywhere
# Usage: ./hei-datahub.sh [args]
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run hei-datahub from the virtual environment
exec "${SCRIPT_DIR}/.venv/bin/hei-datahub" "$@"
