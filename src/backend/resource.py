import json
import logging
import uuid

import falcon
from falcon import Request, Response
from pony.orm import db_session

from .hooks import require_auth
from .models import User, Wallet

log = logging.getLogger(__name__)


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
                'BTC': float(wallet.balance_btc),
                'USD': float(wallet.balance_usd),
            }
        })


wallet_collection = WalletCollectionResource()


@falcon.before(require_auth)
class WalletResource:

    @db_session
    def on_get(self, req: Request, resp: Response, address: str):
        token = req.get_header('Authorization')
        wallet = Wallet.select(
            lambda w: w.address == address and w.user.token == token
        ).first()
        if not wallet:
            raise falcon.HTTPNotFound()
        resp.body = json.dumps({
            'address': address,
            'balance': {
                'BTC': float(wallet.balance_btc),
                'USD': float(wallet.balance_usd),
            }
        })


wallet_item = WalletResource()
