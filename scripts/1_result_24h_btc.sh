#!/bin/bash

# MANUAL INPUTS:
INP_START=1095 # hours back
INP_TIMEFRAME="1h"
INP_PERIOD="24 HOURS"
INP_TAIL=24
INP_TICKER='BTC-USD'
INP_NAME='BITCOIN'

tmux send-keys -t trade_nd:=predictions.0 'C-c'
# tmux send-keys -t trade_nd:=predictions.0 'C-l'
tmux send-keys -t trade_nd:=predictions.0 'clear' enter
tmux send-keys -t trade_nd:=predictions.0 "python3 /root/prophet_predictions_bot/predictions/run_bot_results_crytpo.py $INP_START $INP_TIMEFRAME \"$INP_PERIOD\" $INP_TAIL $INP_TICKER \"$INP_NAME\"" enter # Start the bot