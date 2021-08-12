#!/Users/kevintrng/opt/anaconda3/bin/python3

import yfinance as yf
import datetime as dt
import pandas as pd
from findata import get_intradaydata
import os

current_month = dt.date.today().strftime('%b')
dirpath = os.path.dirname(__file__)
tickers = ['GME','AMC','BB','NOK',"CLOV"]

if __name__ == '__main__':
    get_intradaydata(tickers, p = "1mo", i = "5m").to_csv(os.path.join(dirpath,f'data/fivemin/intra_{current_month}.csv'))
    print(f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Intraday (5min) data downloaded for {', '.join(tickers)}")