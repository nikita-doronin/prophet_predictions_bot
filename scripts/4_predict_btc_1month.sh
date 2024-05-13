#!/bin/bash

# MANUAL INPUTS:
INP_START=1095 # days back
INP_TIMEFRAME="1d"
INP_PERIOD="30 DAYS"
INP_TAIL=30
INP_TICKER="BTC-USD"
INP_PROPHET_PERIODS=30
INP_PROPHET_FREQ="D"
INP_NAME="BITCOIN"

# Calculations:
tmux send-keys -t trade_nd:=predictions.0 'C-c'
# tmux send-keys -t trade_nd:=predictions.0 'C-l'
tmux send-keys -t trade_nd:=predictions.0 'clear' enter
tmux send-keys -t trade_nd:=predictions.0 "python3 /root/prophet_predictions_bot/predictions/run_bot_prediction_crypto.py $INP_START $INP_TIMEFRAME \"$INP_PERIOD\" $INP_TAIL $INP_TICKER $INP_PROPHET_PERIODS \"$INP_PROPHET_FREQ\" \"$INP_NAME\"" enter # Start the bot