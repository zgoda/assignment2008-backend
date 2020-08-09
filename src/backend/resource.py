import json
import uuid
import datetime
import logging
from decimal import Decimal

import falcon
import requests
from requests.exceptions import Timeout, HTTPError
from falcon import Request, Response
from pony.orm import db_session

from .models import User, Wallet
from .hooks import require_auth

log = logging.getLogger(__name__)


class Ticker:

    url = 'https://blockchain.info/ticker'
    rates = {
        'USD': None
    }
    last_fetch = None
    session = requests.Session()

    @classmethod
    def get(cls):
        now = datetime.datetime.utcnow()
        if (
                None in (cls.last_fetch, cls.rates['USD']) or
                now > cls.last_fetch + datetime.timedelta(hours=1)
                ):
            try:
                resp = cls.session.get(cls.url, timeout=(3.05, 9))
                if resp.ok:
                    data = resp.json()
                    cls.rates['USD'] = Decimal(str(data['USD']['last']))
                    cls.last_fetch = now
                else:
                    resp.raise_for_status()
            except Timeout:
                log.warning('exchange rates fetch timed out')
            except HTTPError as e:
                code = e.response.status_code
                log.warning(f'ticker service response {code}')
        if cls.rates['USD']:
            return cls.rates['USD'] / 100000000


class UserCollectionResource:

    @db_session
    def on_post(self, req: Request, resp: Response):
        token = str(uuid.uuid4())
        User(token=token)
        resp.body = json.dumps({'token': token})
        resp.status = falcon.HTTP_201


user_collection = UserCollectionResource()


@falcon.before(require_auth)
class WalletCollectionResource:

    ticker = Ticker()

    @db_session
    def on_post(self, req: Request, resp: Response):
        token = req.get_header('Authorization')
        user = User.select(lambda u: u.token == token).first()
        if user.wallets.count() > 9:
            raise falcon.HTTPForbidden(
                'Max allowed wallets exceeded',
                'Maximum number of allowed wallets already reached',
            )
        address = str(uuid.uuid4())
        wallet = Wallet(user=user, address=address)
        resp.body = json.dumps({
            'address': address,
            'balance': {
                'BTC': wallet.balance / 100000000,
                'USD': float(self.ticker.get() * 100000000),
            }
        })


wallet_collection = WalletCollectionResource()
