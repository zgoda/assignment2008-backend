import os
from decimal import Decimal

from dotenv import find_dotenv, load_dotenv
from pony.orm import Database, Required, Set

from .platform import NotEnoughFunds, WalletNotFound, collect_transaction_fee, get_rate

db = Database()


class User(db.Entity):
    _table_ = 'users'
    token = Required(str, 200, unique=True)
    wallets = Set('Wallet')


class Wallet(db.Entity):
    user = Required(User)
    address = Required(str, 200, unique=True)
    balance = Required(Decimal, precision=64, scale=2, default=Decimal('100000000'))
    transactions_in = Set('Transaction', reverse='tgt_wallet')
    transactions_out = Set('Transaction', reverse='src_wallet')

    @property
    def balance_btc(self):
        return self.balance / Decimal('100000000')

    @property
    def balance_usd(self):
        return self.balance * get_rate()


class Transaction(db.Entity):
    src_wallet = Required(Wallet, reverse='transactions_out')
    tgt_wallet = Required(Wallet, reverse='transactions_in')
    amount = Required(Decimal, precision=64, scale=2)
    fee = Required(Decimal, precision=64, scale=2, default=Decimal('0'))

    @classmethod
    def make_transfer(cls, token: str, from_: str, to_: str, amount: int):
        src_wallet = Wallet.select(  # pragma: no branch
            lambda w: w.address == from_ and w.user.token == token
        ).first()
        if not src_wallet:
            raise WalletNotFound(f'Wallet {from_} not found or is not yours')
        tgt_wallet = Wallet.select(  # pragma: no branch
            lambda w: w.address == to_
        ).first()
        if not tgt_wallet:
            raise WalletNotFound(f'Wallet {to_} not found')
        fee = None
        to_withdraw = Decimal(str(amount))
        if src_wallet.user != tgt_wallet.user:
            fee = Decimal('0.015') * amount
            to_withdraw = amount + fee
        if src_wallet.balance < to_withdraw:
            raise NotEnoughFunds()
        src_wallet.balance = src_wallet.balance - to_withdraw
        tgt_wallet.balance = tgt_wallet.balance + amount
        extra = {}
        if fee:
            collect_transaction_fee(fee)
            extra['fee'] = fee
        cls(src_wallet=src_wallet, tgt_wallet=tgt_wallet, amount=amount, **extra)


load_dotenv(find_dotenv())

db.bind(
    provider='postgres', user=os.getenv('PGUSER'), password=os.getenv('PGPASSWORD'),
    host=os.getenv('PGHOST'), database=os.getenv('PGDATABASE'),
)
db.generate_mapping(create_tables=True)
