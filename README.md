# README

## Disclaimer
This software for prices prediction is provided as-is, without any warranties or guarantees of its performance. The author is not responsible for any losses incurred through the use of this software. Users are advised to conduct their own research and exercise caution when using this strategy. The prediction logic in this software is not financial advice, and users should seek professional financial advice before making any investment decisions.

## Legal statement
The source code is protected by **Attribution-NonCommercial (CC BY-NC)** license.
The **`LICENCE`** itself could be found in repository root directory.

This license allows others to distribute, remix, adapt, and build upon my work non-commercially, as long as they give me credit for the original creation and indicate if changes were made. This license prohibits the use of my work for commercial purposes without my explicit permission.

Using third-party Python libraries in my project does not necessarily mean my entire project adopts the same license as those libraries. When I use a library in my project, I am typically using it as a dependency. The license I choose for my project affects only my code and original trading idea, not the libraries I use.

## Project description
Main core of this project is [Meta Prophet](https://facebook.github.io/prophet/docs/quick_start.html) library for time series forecasting.

Prophet is a procedure for forecasting time series data based on an additive model where non-linear trends are fit with yearly, weekly and daily seasonality. The implementation comes with support for linear and exponential smoothing methods.

The presented project will automatically preapre a price forecast of asset and send it to telegram group or chat.

## Live project examples
Check the real live predictions in [TradeND Telegram group](https://t.me/trade_ND)

## Main script
The script logic could be found here:
`root/prophet_predictions_bot/script_logic/script_logic.drawio`.

You may be using [drawio](https://www.drawio.com/) to open the file. Otherwise you could open the **.png** file:

![Alt text](https://github.com/nikita-doronin/prophet_predictions_bot/blob/main/script_logic/script_logic.drawio.png)

## Set up the project
1. In case of new Linux server run the `sudo apt update` in [Linux Shell](https://wiki.debian.org/Shell#:~:text=Debian%20uses%20Bash%20as%20the,the%20file%20%2Fetc%2Fadduser.), after that run `sudo apt upgrade`.

2. Make sure that  **tmux**, **htop** and **pip** are installed via running `sudo apt install tmux htop pip` in **Linux Shell**.

3. Create a virtual environment via running `python3 -m venv .predictions_venv` in **Linux Shell**.

4. Activate the virtual environment via running `source .predictions_venv/bin/activate` in **Linux Shell**.

5. Install the requirements via running `pip install -r /root/prophet_predictions_bot/requirements.in` in **Linux Shell**.

6. For the first time run the `bash /root/prophet_predictions_bot/scripts/0_1_server_update.sh` in **Linux Shell** to update the server.

7. For the first time run the `bash /root/prophet_predictions_bot/scripts/0_2_tmux_start.sh` in **Linux Shell** to start the **tmux** session.

8. For the first time run the `bash /root/prophet_predictions_bot/scripts/0_3_activate_venv.sh` in **Linux Shell** to activate the virtual environment.

9. Set up the credentials `/root/prophet_predictions_bot/set_creds/set_creds.ipynb` for:

    - **Telegram bot:**
        - telegram_token_id
        - telegram_chat_id

10. Prepare **Bash Scripts** to run the predictions automatically via **Cron Job**. Examples of **Bash Scripts** could be found under folder `/root/prophet_predictions_bot/scripts`.
    - Bash Scripts may contain the following variables that will be passed to the python scripts as inputs values:
        - **INP_START** - integer, number of bars/candles back.
        - **INP_TIMEFRAME** - string, timeframe for the dataframe.
        - **INP_PERIOD** - string, the text that will be used in telegram posts.
        - **INP_TAIL** - integer, number of last bars/candles to include in the dataframe.
        - **INP_TICKER** - string, asset you want to predict, use the format from **Yahoo Finance**.
        - **INP_PROPHET_PERIODS** - integer, number of periods to predict, technical input for Prophet.
        - **INP_PROPHET_FREQ** - string, frequency/timeframe of the prediction, technical input for Prophet.
        - **INP_NAME** - string, name of the asset that will be used in telegram posts.

11. Open the **Cron Job** daemon via running `crontab -e` in **Linux Shell** and set up the Cron Jobs on your required time. Cron Job will execute predictions automatically. The example of Cron Jobs:
![Alt text](https://github.com/nikita-doronin/prophet_predictions_bot/blob/main/crontab.png)
