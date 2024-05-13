#!/bin/bash

#https://dimon.ca/how-to-setup-ibc-and-tws-on-headless-ubuntu-in-10-minutes/#h.udghm8581dwb

# downloads and installs the updates:
sudo apt update
sudo apt -y upgrade

# clears out the local repository of retrieved package files:
sudo apt clean
sudo apt autoclean
sudo apt -y autoremove

# clear the terminal:
tmux send-keys 'clear' enter

# Activate the virtual environment:
# Define the path to your virtual environment:
VIRTUAL_ENV_PATH="/root/.predictions_venv"

# Check if the virtual environment directory exists:
if [ -d "$VIRTUAL_ENV_PATH" ]; then
    # Activate the virtual environment
    source "$VIRTUAL_ENV_PATH/bin/activate"
    echo "Virtual environment activated."
else
    echo "Error: Virtual environment directory not found"
    sudo apt install python3.11-venv
    python3 -m venv .predictions_venv
    source /root/.predictions_venv/bin/activate
    echo "Virtual environment created and activated."
fi

# update pip and all libraries:
pip install --upgrade pip # update pip
pip-review --local --auto # update all libraries

# deactivate the Virtual environment:
deactivate

# drop caches
sync; echo 3 | sudo tee /proc/sys/vm/drop_caches
sync; echo 2 | sudo tee /proc/sys/vm/drop_caches
sync; echo 1 | sudo tee /proc/sys/vm/drop_caches

# clean the terminal:
clear