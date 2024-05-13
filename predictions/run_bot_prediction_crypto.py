import os, sys
import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import keyring as kr
from datetime import datetime, timedelta
from prophet import Prophet
from numerize import numerize

# Settings coming from bash:
inp_start = int(sys.argv[1])
inp_timeframe = sys.argv[2]
inp_period = sys.argv[3]
inp_tail = int(sys.argv[4])
inp_ticker = sys.argv[5]
inp_prophet_periods = int(sys.argv[6])
inp_prophet_freq = sys.argv[7]
inp_name=sys.argv[8]

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

def prepare_data(data):
    global last_close
    # Data preparation:
    data = data.reset_index(drop=False)

    if "Datetime" in data.columns:
        data=data.rename(columns={'Datetime': 'Date'})

    data['OHLC/4'] = (data["Close"]+data["Open"]+data["High"]+data["Low"])/4
    data = data[["Date","OHLC/4"]] # yahoo finance version

    data["New_date"]=data['Date'].dt.tz_localize(None)
    data = data.rename(columns = {"New_date":"ds","OHLC/4":"y"})

    last_close=data['y'].iloc[-1] # get the close price of the last available candle to move/fit the prediction channel
    return data

def predict_prophet(data,inp_prophet_periods,inp_prophet_freq):
    # Prophet Calculations:
    m = Prophet()
    m.fit(data)

    if inp_timeframe == '1d':
        future = m.make_future_dataframe(periods=inp_prophet_periods)
    else:
        future = m.make_future_dataframe(periods=inp_prophet_periods, freq=inp_prophet_freq)

    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
    del m, future
    return forecast

def finish_data(forecast):
    global t
    # Create a DataFrame From Prediction:
    df = pd.DataFrame()
    df = df.reset_index()
    df['ds'] = forecast['ds']#.tail(inp_tail)
    df['Lower Band'] = forecast['yhat_lower']#.tail(inp_tail)
    df['Upper Band'] = forecast['yhat_upper']#.tail(inp_tail)
    df['yhat'] = forecast['yhat']#.tail(inp_tail)
    df = df.set_index(df['ds'])

    # Get the close price of the first value of Middle Band (yhat) to move/fit the prediction channel:
    last_close_prediction=df['yhat'].tail(inp_tail).iloc[0]

    # Move/fit the prediction channel:
    if last_close >= last_close_prediction: # in case the prediction channel is below the current price
        close_differece = last_close-last_close_prediction
        df['Lower Band'] = df['Lower Band'] + close_differece
        df['Upper Band'] = df['Upper Band'] + close_differece
        df['yhat'] = df['yhat'] + close_differece

    if last_close < last_close_prediction: # in case the prediction channel is above the current price
        close_differece = last_close_prediction-last_close
        df['Lower Band'] = df['Lower Band'] - close_differece
        df['Upper Band'] = df['Upper Band'] - close_differece
        df['yhat'] = df['yhat'] - close_differece

    # Save to parquet for further results:
    df.tail(inp_tail).to_parquet(f'{path}/tech/data/{inp_ticker}_predict_{inp_tail}_{inp_timeframe}.parquet')

    # Calculate text for the text post:
    ll_now=df.iloc[-30]['Lower Band']
    hh_now=df.iloc[-30]['Upper Band']

    ll_after=df.iloc[-1]['Lower Band']
    hh_after=df.iloc[-1]['Upper Band']

    if (ll_now < ll_after) and (hh_now < hh_after):
        trend='📈 Up Trend'
    elif (ll_now > ll_after) and (hh_now > hh_after):
        trend='📉 Down Trend'
    else:
        trend='Flat'

    ll_now=numerize.numerize(df.iloc[-30]['Lower Band'])
    hh_now=numerize.numerize(df.iloc[-30]['Upper Band'])

    ll_after=numerize.numerize(df.iloc[-1]['Lower Band'])
    hh_after=numerize.numerize(df.iloc[-1]['Upper Band'])

    t=f"{inp_name} - 🤖 PRICE PREDICTION BY NEURAL NETWORK 🤖 - NEXT {inp_period} \
    \n \n{trend} \
    \n \nLowest point in 1 hour: {ll_now} \
    \nHighest point in 1 hour1: {hh_now} \
    \n \nLowest point in 24 hours: {ll_after} \
    \nHighest point in 24 hours: {hh_after} \
    \n\nThis post was automatically generated by TradeND bot \
    \n\nSupport the project (TRC20): \
    \nTXh97eZirBuvUfMPqECZgWUPCTefTSNwBg"

    del last_close_prediction, ll_now, hh_now, ll_after, hh_after

    return df

def create_chart(df,dff):
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
        title=("AI Prediction for: "+inp_ticker+", next "+inp_period), # title of the plot
        legend = dict(orientation = 'h', xanchor = "right", x = 1, y= 1.22) # to change legend position
    )

    # Show and save figure:
    # fig.show()
    img_path=f"{path}/tech/pic/{inp_ticker}_predict_{inp_tail}_{inp_timeframe}.png"
    fig.write_image(img_path)
    return img_path

if __name__ == "__main__":
    get_saved_creds()
    while True:
        try:
            get_script_directory()
            data = get_data(inp_ticker=inp_ticker, inp_timeframe=inp_timeframe)
            dff = create_candlestick(data=data)
            data = prepare_data(data=data)
            forecast = predict_prophet(data=data, inp_prophet_periods=inp_prophet_periods, inp_prophet_freq=inp_prophet_freq)
            del data
            df = finish_data(forecast=forecast)
            del forecast
            img_path=create_chart(df=df, dff=dff)
            del df, dff
            send_image(inp_bot_token=telegram_token_id, inp_id=telegram_chat_id, img=img_path, text=t)
            break
        except Exception as e:
            print(e)
            pass