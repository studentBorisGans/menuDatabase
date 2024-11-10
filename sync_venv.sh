#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing/updating dependencies from requirements.txt..."
    pip install -r requirements.txt
    echo "Dependencies installed/updated."
else
    echo "requirements.txt not found!"
fi

# Deactivate the virtual environment after installation
deactivate
