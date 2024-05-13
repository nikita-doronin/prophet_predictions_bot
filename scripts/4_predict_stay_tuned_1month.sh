#!/bin/bash

tmux send-keys -t trade_nd:=predictions.0 'C-c'
# tmux send-keys -t trade_nd:=predictions.0 'C-l'
tmux send-keys -t trade_nd:=predictions.0 'clear' enter
tmux send-keys -t trade_nd:=predictions.0 'python3 /root/prophet_predictions_bot/predictions/stay_tuned_1month.py' enter # Start the bot