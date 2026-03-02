#!/bin/zsh
# Create and activate Python virtual environment, then install dependencies
/opt/homebrew/bin/python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Alias to run the tool easily
alias csvimport='python3 "$HOME/csvimport/csvimport.py"'
