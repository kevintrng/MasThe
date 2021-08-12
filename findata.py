#!/Users/kevintrng/opt/anaconda3/bin/python3

import yfinance as yf
import pandas as pd
import os
import datetime as dt

def get_optionchain(ticker, expiry):
    '''
    Returns pandas DataFrame with option chain downloaded from Yahoo Finance
    
    
    Args:
    --------------
    ticker: str
        Yahoo Finance ticker
    expiry: str in format yyyy-mm-dd
        Expiry date of options
    '''
    option_chain = [df.set_index('contractSymbol') for df in yf.Ticker(ticker).option_chain(expiry)]
    return pd.concat(option_chain, keys = ['CALLS','PUTS'])

def get_intradaydata(tickers, p, i):
    '''
    Returns intraday data from Yahoo Finance for specified period and interval
    
    Args:
    ---------------
    p: str
        Period
    i: str
        Interval (1m, 5m, 1d, 1m, etc.). '1m' intervals returns only up to last 7days. Five minute
        data is kept up to date for 30days
    '''
    return yf.download(" ".join(tickers), period = p, interval = i)


def main():
    dt_today = dt.date.today().strftime("%Y-%m-%d")
    dirpath = os.path.dirname(__file__)
    tickers = ['GME','AMC','BB','NOK',"CLOV"]
    
    ### Get intraday data for GME, AMC, BB, NOK, CLOV
    get_intradaydata(tickers, '7d','1m').to_csv(os.path.join(dirpath,f'data/intraday/intraday_{dt_today}.csv'))

    ###Get option chains for GME, AMC and BB
    for ticker in tickers[:3]:
        get_optionchain(ticker, dt_today).to_csv(os.path.join(dirpath,f'data/options/{ticker.lower()}_optchain_{dt_today}.csv'))


    
if __name__ == '__main__':
    ###Run script
    main()
    print(f'{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Weekly option chains and intraday data successfully downloaded')
