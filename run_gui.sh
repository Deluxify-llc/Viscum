#!/bin/bash
echo "Starting Viscum GUI..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if virtual environment exists, if so use it
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "Using virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
    python ViscumGUI.py
    exit $?
fi

# Try to use python3, fallback to system Python on macOS if tkinter not available
if python3 -c "import tkinter" 2>/dev/null; then
    python3 ViscumGUI.py
elif [[ "$OSTYPE" == "darwin"* ]] && /usr/bin/python3 -c "import tkinter" 2>/dev/null; then
    echo "Using system Python (Homebrew Python lacks tkinter)..."
    /usr/bin/python3 ViscumGUI.py
else
    echo "Error: tkinter not found. Please install python3-tk or use a Python with tkinter support."
    exit 1
fi
