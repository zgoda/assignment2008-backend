from decimal import Decimal

import responses
from requests.exceptions import Timeout

from backend import platform

TICKER_URL = 'https://blockchain.info/ticker'


def test_get_rate_ok(mocked_responses):
    platform.rates['_last_fetch'] = None
    value = 10
    mocked_responses.add(responses.GET, TICKER_URL, json={'USD': {'last': value}})
    rate = platform.get_rate()
    assert rate == Decimal(value) / Decimal(100000000)


def test_get_rate_server_error(mocked_responses, caplog):
    platform.rates['_last_fetch'] = None
    mocked_responses.add(responses.GET, TICKER_URL, status=503)
    platform.get_rate()
    assert 'response 503' in caplog.text


def test_get_rate_timeout(mocked_responses, caplog):
    platform.rates['_last_fetch'] = None
    mocked_responses.add_callback(responses.GET, TICKER_URL, callback=Timeout)
    platform.get_rate()
    assert 'timed out' in caplog.text
