import os, sys
import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import keyring as kr
from datetime import datetime, timedelta

# Settings coming from bash:
inp_start=int(sys.argv[1])
inp_timeframe=sys.argv[2]
inp_period=sys.argv[3]
inp_tail=int(sys.argv[4])
inp_ticker=sys.argv[5]
inp_name=sys.argv[6]

def get_script_directory():
    # Get the path of the directory containing the currently running script:
    global path
    try:
        path = os.path.dirname(os.path.realpath(__file__))
        return path
    except:
        sys.exit()

def get_saved_creds():
    # get credentials that where generated at 'set_creds.ipynb':
    global telegram_chat_id,telegram_token_id
    try:
        telegram_chat_id = kr.get_password("telegram_creds",'telegram_chat_id')
        telegram_token_id = kr.get_password("telegram_creds",'telegram_token_id')
        return telegram_chat_id,telegram_token_id
    except:
        sys.exit()

def send_image(inp_bot_token, inp_id, img, text):
    # Send post with image to telegram
    url = 'https://api.telegram.org/bot'+inp_bot_token+'/sendPhoto'
    f = {'photo' : open(file=img, mode='rb')}
    d = {'chat_id' : inp_id, 'caption' : text}
    response = requests.get(url, files = f, data = d)
    r = response.json()
    return r

def get_data(inp_ticker, inp_timeframe):
    # Calculate the start time:
    end_time = datetime.utcnow()
    if inp_timeframe == '1d':
        start_time = end_time - timedelta(days=inp_start)
    else:
        start_time = end_time - timedelta(hours=inp_start)

    # Convert start and end times to strings in UTC format:
    start_time_str = start_time.strftime('%Y-%m-%d')

    # Download data for a specific stock symbol:
    data = yf.download(inp_ticker, start=start_time_str, end=None, interval=inp_timeframe, progress=False)

    # Filter ther data to only include data after start_time:
    data = data[(data.index > start_time.strftime('%Y-%m-%d %H:%M:%S'))]

    del end_time, start_time, start_time_str
    return data

def create_candlestick(data):
    # Create a DataFrame for OHLC Candlestick:
    dff = pd.DataFrame()
    dff['Open'] = data['Open'].tail(150)
    dff['High'] = data['High'].tail(150)
    dff['Low'] = data['Low'].tail(150)
    dff['Close'] = data['Close'].tail(150)
    dff = dff.reset_index(drop=False)

    if "Datetime" in dff.columns:
        dff=dff.rename(columns={'Datetime': 'Date'})

    return dff

def create_chart(dff):
    # Read the last prediction:
    df = pd.read_parquet(f'{path}/tech/data/{inp_ticker}_predict_{inp_tail}_{inp_timeframe}.parquet')

    # Create a figure:
    fig = go.Figure()

    # Add a candlestick chart:
    fig.add_trace(go.Candlestick(x=dff['Date'],
                    open=dff['Open'],
                    high=dff['High'],
                    low=dff['Low'],
                    close=dff['Close'],name="Candlestick"))

    # Add bands:
    fig.add_trace(go.Scatter(x=df['ds'].tail(inp_tail), y=df['yhat'].tail(inp_tail), mode='lines', name='Mid Band',line=dict(color='rgb(251,128, 114)')))
    fig.add_trace(go.Scatter(x=df['ds'].tail(inp_tail), y=df['Lower Band'].tail(inp_tail), mode='lines', name='Lower Band',line=dict(color='rgb(251,128, 114)')))
    fig.add_trace(go.Scatter(x=df['ds'].tail(inp_tail), y=df['Upper Band'].tail(inp_tail),fill='tonexty', mode='lines', name='Upper Band',line=dict(color='rgb(251,128, 114)')))

    # Add logo if needed:
    # fig.add_layout_image(
    #     dict(
    #         source=f"{path}/tech/logo.png",
    #         xref="paper", yref="paper",
    #         x=0.7, y=0.1,
    #         sizex=0.9, sizey=0.9,
    #         xanchor="right", yanchor="bottom",
    #         opacity=0.1
    #     )
    # )

    # Update layout:
    fig.update_layout(
        showlegend=True,
        xaxis_rangeslider_visible=False, # hide slidebar
        autosize=True,
        height=500,
        width=1100,
        title=("Result of AI Prediction for: "+inp_name+", past "+inp_period), # title of the plot
        legend = dict(orientation = 'h', xanchor = "right", x = 1, y= 1.22) # to change legend position
    )

    # Show and save figure:
    # fig.show()
    img_path=f"{path}/tech/pic/{inp_ticker}_result_{inp_tail}_{inp_timeframe}.png"
    fig.write_image(img_path)
    return img_path

def define_message():
    t=f" ➡️ Result of {inp_name} Short-term prediction made {inp_period} ago ➡️ \
    \n\nThis post was automatically generated by TradeND bot \
    \n\nSupport the project (TRC20): \
    \nTXh97eZirBuvUfMPqECZgWUPCTefTSNwBg"
    return t

if __name__ == "__main__":
    get_saved_creds()
    while True:
        try:
            get_script_directory()
            data = get_data(inp_ticker=inp_ticker, inp_timeframe=inp_timeframe)
            dff = create_candlestick(data=data)
            del data
            img_path=create_chart(dff=dff)
            del dff
            t = define_message()
            send_image(inp_bot_token=telegram_token_id, inp_id=telegram_chat_id, img=img_path, text=t)
            break
        except Exception as e:
            print(e)
            pass
    