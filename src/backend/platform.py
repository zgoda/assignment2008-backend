import datetime
import logging
from decimal import Decimal

from requests import Session
from requests.exceptions import HTTPError, Timeout

log = logging.getLogger(__name__)

rates = {
    '_last_fetch': None,
    'USD': None,
}

session = Session()


def get_rate():
    ticker_url = 'https://blockchain.info/ticker'
    now = datetime.datetime.utcnow()
    if (
            None in (rates['_last_fetch'], rates['USD']) or
            now > rates['_last_fetch'] + datetime.timedelta(hours=1)
            ):
        try:
            resp = session.get(ticker_url, timeout=(3.05, 9))
            if resp.ok:
                data = resp.json()
                rates['USD'] = Decimal(str(data['USD']['last'])) / Decimal(100000000)
                rates['_last_fetch'] = now
            else:
                resp.raise_for_status()
        except Timeout:
            log.warning('exchange rates fetch timed out')
        except HTTPError as e:
            code = e.response.status_code
            log.warning(f'ticker service response {code}')
    return rates['USD']
