import json
import uuid

import falcon
from falcon import Request, Response
from pony.orm import db_session

from .models import User


class UserCollectionResource:

    @db_session
    def on_post(self, req: Request, resp: Response):
        while True:
            token = str(uuid.uuid4())
            q = (u.token for u in User if u.token == token)
            if not q.count():
                break
        User(token=token)
        resp.body = json.dumps({'token': token})
        resp.status = falcon.HTTP_201


user_collection = UserCollectionResource()
