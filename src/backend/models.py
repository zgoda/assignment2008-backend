import os

from pony.orm import Database, Required, Set

db = Database()


class User(db.Entity):
    token = Required(str, 200, unique=True)
    wallets = Set('Wallet')


class Wallet(db.Entity):
    user = Required(User)
    address = Required(str, 200, unique=True)
    balance = Required(int, default=100000000)
    transactions_in = Set('Transaction', reverse='tgt_wallet')
    transactions_out = Set('Transaction', reverse='src_wallet')

    def balance_values(self):
        return {
            'BTC': self.balance * 100000000,
        }


class Transaction(db.Entity):
    src_wallet = Required(Wallet, reverse='transactions_out')
    tgt_wallet = Required(Wallet, reverse='transactions_in')
    amount = Required(int)
    fee = Required(int, default=0)


db.bind(
    provider='postgres', user=os.getenv('PGUSER'), password=os.getenv('PGPASSWORD'),
    host=os.getenv('PGHOST'), database=os.getenv('PGDATABASE'),
)
db.generate_mapping(create_tables=True)
