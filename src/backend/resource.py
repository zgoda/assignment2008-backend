import json
import uuid
import datetime
from decimal import Decimal

import falcon
import requests
from falcon import Request, Response
from pony.orm import db_session, select

from .models import User, Wallet
from .hooks import require_auth


class Ticker:

    url = 'https://blockchain.info/ticker'
    rates = {
        'USD': None
    }
    last_fetch = None
    session = requests.Session()

    @classmethod
    def get(cls, currency):
        now = datetime.datetime.utcnow()
        if (
                None in (cls.last_fetch, cls.rates['USD']) or
                now > cls.last_fetch + datetime.timedelta(hours=1)
                ):
            resp = cls.session.get(cls.url)
            if resp.ok:
                data = resp.json()
                cls.rates['USD'] = Decimal(str(data['USD']['last']))
                cls.last_fetch = now
        return cls.rates['USD'] / 100000000


class UserCollectionResource:

    @db_session
    def on_post(self, req: Request, resp: Response):
        while True:
            token = str(uuid.uuid4())
            if not select(u.token for u in User if u.token == token).count():
                break
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
        while True:
            address = str(uuid.uuid4())
            if not select(
                        w.address
                        for w in Wallet
                        if w.user == user and w.address == address
                    ).count():
                break
        wallet = Wallet(user=user, address=address)
        resp.body = json.dumps({
            'address': address,
            'balance': {
                'BTC': wallet.balance / 100000000,
                'USD': float(self.ticker.get('USD') * 100000000),
            }
        })


wallet_collection = WalletCollectionResource()
