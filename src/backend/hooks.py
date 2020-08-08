import falcon
from falcon import Request, Response
from pony.orm import db_session, select

from .models import User


@db_session
def require_auth(req: Request, resp: Response, resource, params: dict):
    token = req.get_header('Authorization')
    if not token:
        raise falcon.HTTPUnauthorized('Missing token', 'Authorization token missing')
    if not select(u.token for u in User if u.token == token).count():
        raise falcon.HTTPUnauthorized(
            'Invalid token', 'Provided token is not recognized as valid'
        )
