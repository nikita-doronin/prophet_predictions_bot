#!/bin/bash

# INPUT the name of the virtual environment:
VIRTUALENV_NAME=".predictions_venv"

# Activate the virtual environment in the dedicated tmux window:
tmux send-keys -t trade_nd:=predictions.0 "source $VIRTUALENV_NAME/bin/activate" C-m