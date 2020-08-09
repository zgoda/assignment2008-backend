import falcon

from .resource import user_collection, wallet_collection, wallet_item

app = falcon.API()

app.add_route('/users', user_collection)
app.add_route('/wallets', wallet_collection)
app.add_route('/wallets/{address}', wallet_item)
