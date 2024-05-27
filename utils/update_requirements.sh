#!/bin/sh

# Update the requirements.txt file using pip freeze
echo "Updating requirements.txt..."
pip freeze > requirements.txt
echo "requirements.txt updated."

