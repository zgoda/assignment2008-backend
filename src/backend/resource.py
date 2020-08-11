import json
import logging
import uuid

import falcon
from falcon import Request, Response
from pony.orm import db_session, select

from .hooks import require_auth, require_admin
from .models import User, Wallet, Transaction
from .platform import WalletNotFound, NotEnoughFunds

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
        user = select(  # pragma: no branch
            u for u in User if u.token == req.auth
        ).first()
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
        wallet = select(  # pragma: no branch
            w for w in Wallet if w.address == address and w.user.token == req.auth
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


@falcon.before(require_auth)
class TransactionCollectionResource:

    @db_session
    def on_get(self, req: Request, resp: Response):
        transactions = select(  # pragma: no branch
            t for t in Transaction if
            t.src_wallet.user.token == req.auth or t.tgt_wallet.user.token == req.auth
        )
        resp.body = json.dumps([
            {
                'amount': float(t.amount),
                'fee': float(t.fee),
                'from': t.src_wallet.address,
                'to': t.tgt_wallet.address
            } for t in transactions
        ])

    @db_session
    def on_post(self, req: Request, resp: Response):
        from_addr = req.media.get('from')
        to_addr = req.media.get('to')
        amount = req.media.get('amount')
        error_resp = {}
        try:
            Transaction.make_transfer(req.auth, from_addr, to_addr, amount)
        except WalletNotFound as e:
            error_resp.update({
                'code': 'WALLET_NOT_FOUND',
                'message': str(e)
            })
        except NotEnoughFunds:
            error_resp.update({
                'code': 'NOT_ENOUGH_FUNDS',
                'message': (
                    f'There is not enough funds in your wallet {from_addr} '
                    'to complete this transaction'
                )
            })
        if error_resp:
            resp.body = json.dumps({
                'error': error_resp
            })
            resp.status = falcon.HTTP_400
        else:
            resp.status = falcon.HTTP_201


transaction_collection = TransactionCollectionResource()


@falcon.before(require_auth)
class WalletTransactionsCollectionResource:

    @db_session
    def on_get(self, req: Request, resp: Response, address: str):
        transactions = Transaction.select(  # pragma: no branch
            lambda t: (
                (
                    t.src_wallet.user.token == req.auth or
                    t.tgt_wallet.user.token == req.auth
                )
                and
                (t.src_wallet.address == address or t.tgt_wallet.address == address)
            )
        )[:]
        resp.body = json.dumps([
            {
                'amount': float(t.amount),
                'fee': float(t.fee),
                'from': t.src_wallet.address,
                'to': t.tgt_wallet.address,
                'type': 'OUT' if t.src_wallet.address == address else 'IN',
            } for t in transactions
        ])


wallet_transactions_collection = WalletTransactionsCollectionResource()


@falcon.before(require_admin)
class StatisticsResource:

    @db_session
    def on_get(self, req: Request, resp: Response):
        fees = select(sum(t.fee) for t in Transaction).first()  # pragma: no branch
        tr_count = Transaction.select().count()
        resp.body = json.dumps({
            'transactions': tr_count,
            'profit': float(fees),
        })


statistics = StatisticsResource()
