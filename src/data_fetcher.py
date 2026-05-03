import pandas as pd
from datetime import date

from src.kite_client import get_kite


def get_weekly_nifty_tokens():
    kite = get_kite()
    instruments = pd.DataFrame(kite.instruments("NFO"))

    nifty = instruments[(instruments['name'] == 'NIFTY') & (instruments['instrument_type'].isin(['CE','PE']))]
    nifty['expiry'] = pd.to_datetime(nifty['expiry']).dt.date

    upcoming = sorted([e for e in nifty['expiry'].unique() if e >= date.today()])[0]
    weekly = nifty[nifty['expiry'] == upcoming]

    return weekly[['instrument_token','strike','instrument_type']]
