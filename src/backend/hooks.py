import os

import falcon
from falcon import Request, Response
from pony.orm import db_session, select

from .models import User


@db_session
def require_auth(req: Request, resp: Response, resource, params: dict):
    if not req.auth:
        raise falcon.HTTPUnauthorized('Missing token', 'Authorization token missing')
    if not select(u for u in User if u.token == req.auth).first():  # pragma: no branch
        raise falcon.HTTPUnauthorized(
            'Invalid token', 'Provided token is not recognized as valid'
        )


def require_admin(req: Request, resp: Response, resource, params: dict):
    if req.auth != os.environ['ADMIN_TOKEN']:
        raise falcon.HTTPUnauthorized(
            'Admin token required', 'Admin authorization token required'
        )
