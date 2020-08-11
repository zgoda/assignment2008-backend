import falcon

from .resource import (
    statistics, transaction_collection, user_collection, wallet_collection, wallet_item,
    wallet_transactions_collection,
)

app = falcon.API()

app.add_route('/users', user_collection)
app.add_route('/wallets', wallet_collection)
app.add_route('/wallets/{address}', wallet_item)
app.add_route('/wallets/{address}/transactions', wallet_transactions_collection)
app.add_route('/transactions', transaction_collection)
app.add_route('/statistics', statistics)
