import falcon

from .resource import user_collection


app = falcon.API()

app.add_route('/users', user_collection)
