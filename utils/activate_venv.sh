#!/bin/sh

# Activate the virtual environment
echo "Activating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
echo "Virtual environment activated. Run 'deactivate' to deactivate it."
