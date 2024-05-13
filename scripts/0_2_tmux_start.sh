#!/bin/bash

export DISPLAY=:0

tmux new -d -s trade_nd #create a new session

for i in monitor predictions #loop all the process and make it for every user
do  
    tmux new-window -n $i -t trade_nd #create a new window
    tmux split-window -t trade_nd:=$i -h #to split vertically
    # tmux split-window -t trade_nd:=$i -v #to split horizontally
done

sleep 3
tmux send-keys -t trade_nd:=monitor.1 'htop' # start htop in monitor
tmux send-keys -t trade_nd:=monitor.1 enter

# set up the mouse so we can use it in terminal:
tmux send-keys -t trade_nd:=monitor.0 'tmux set -g mouse on' enter