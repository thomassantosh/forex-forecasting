"""Retrieve ticker data"""
import logging
import datetime as dt
from datetime import datetime
import yfinance as yf
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def get_ticker_data(ticker=None):
    """Return ticker data"""
    data = None
    try:
        company = [symbol]
        for i in company:
            data = yf.download(
                    tickers=ticker,
                    interval='1d',
                    start='2020-01-01',
                    end='2021-01-31').reset_index()
            #data.columns=data.columns.str.lower()
            #data.columns=data.columns.str.replace(' ','')
            #data = data.to_json() # converts to a string
        logging.info('Successfully received ticker data.')
    except Exception as e:
        logging.warning(f'Exception: {e}. Failed to load ticker data.')
    finally:
        if data is None:
            final_value = 'No data returned.'
        else:
            final_value = data
    return final_value

if __name__ == "__main__":
    symbol = 'INR=X'
    ticker_history = get_ticker_data(ticker=symbol)
    ticker_history.to_csv('./../datasets/' + str(symbol) +'_ticker_data.csv', index=False, encoding='utf-8')
    print(ticker_history)
