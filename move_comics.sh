#!/bin/bash

# ==============================================================================
# move_comics.sh
# ==============================================================================
# Transfers annotated comic assets from museimages storage (~/Documents/comics)
# to the thinkingbuffer Astro blog and generates/updates the local blog post.
#
# Usage:
#   ./move_comics.sh intro                        # Transfers Introduction assets
#   ./move_comics.sh <book_num> <chapter_num>     # Transfers Book X, Chapter Y
#   ./move_comics.sh 1 0                          # Transfers Introduction (Chapter 0)
#   ./move_comics.sh 1 1                          # Transfers Book 1, Chapter 1
#   ./move_comics.sh 1 1 --move                   # Moves instead of copying
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_HELPER="${SCRIPT_DIR}/.agents/scripts/generate_local_comic.py"

if [ "$#" -eq 0 ]; then
    echo "Usage: ./move_comics.sh <book_number> <chapter_number> [--move]"
    echo "       ./move_comics.sh intro [--move]"
    echo "Examples:"
    echo "  ./move_comics.sh intro"
    echo "  ./move_comics.sh 1 0"
    echo "  ./move_comics.sh 1 2"
    exit 1
fi

if [ -f "$PYTHON_HELPER" ]; then
    python3 "$PYTHON_HELPER" "$@"
else
    echo "Error: Python helper script not found at $PYTHON_HELPER"
    exit 1
fi
