#!/Users/kevintrng/opt/anaconda3/bin/python3

import yfinance as yf
import datetime as dt
import pandas as pd
from findata import get_intradaydata
import os
import sys

dirpath = os.path.dirname(__file__)
tickers = ['GME','AMC','BB','NOK',"CLOV"]

if __name__ == '__main__':
    data = pd.read_csv(os.path.join(dirpath,'data/fivemin/intra_data.csv'), index_col = 0, header = [0,1], parse_dates = True)
    last_update = dt.datetime.fromtimestamp(os.stat(os.path.join(dirpath,'data/fivemin/intra_data.csv')).st_mtime)
    start_date = data.index.max().date()
    end_date = dt.date.today()-dt.timedelta(days = 1)
    
    if (end_date-start_date).days < 3:
        sys.exit("ABORTED: Data have been updated in the last 2 days")
    
    updated_data = yf.download(" ".join(tickers), interval = '5m', start = start_date, end = end_date)
    data = pd.concat([data, updated_data], axis = 0)
    
    data.to_csv(os.path.join(dirpath,'data/fivemin/intra_data.csv'))
    
    print(f"Last Updated on {last_update.strftime('%Y-%m-%d %H:%M')}")
    print(f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Intraday (5min) data downloaded for {', '.join(tickers)}")
    
    if (dt.datetime.now()-last_update).days >= 30:
        print(f"WARNING: SOME DATA MAY BE MISSING. DATA HAS NOT BEEN UPDATED IN MORE THAN A MONTH!!!")
    