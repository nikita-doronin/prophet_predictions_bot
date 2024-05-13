#!/bin/bash

tmux send-keys -t trade_nd:=monitor.0 'C-c'
tmux send-keys -t trade_nd:=monitor.0 'clear' enter
tmux send-keys -t trade_nd:=monitor.0 'sync; echo 3 | sudo tee /proc/sys/vm/drop_caches' enter
sleep 2
tmux send-keys -t trade_nd:=monitor.0 'sync; echo 2 | sudo tee /proc/sys/vm/drop_caches' enter
sleep 2
tmux send-keys -t trade_nd:=monitor.0 'sync; echo 1 | sudo tee /proc/sys/vm/drop_caches' enter