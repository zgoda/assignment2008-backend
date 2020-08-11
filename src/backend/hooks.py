import os

import falcon
from falcon import Request, Response
from pony.orm import db_session, select

from .models import User


@db_session
def require_auth(req: Request, resp: Response, resource, params: dict):
    """Request hook that ensures client is authenticated and is valid.

    :param req: request object
    :type req: Request
    :param resp: response object
    :type resp: Response
    :param resource: resource object serving this request
    :type resource: Any
    :param params: request params
    :type params: dict
    :raises falcon.HTTPUnauthorized: if token is missing or invalid
    """
    if not req.auth:
        raise falcon.HTTPUnauthorized('Missing token', 'Authorization token missing')
    if not select(u for u in User if u.token == req.auth).first():  # pragma: no branch
        raise falcon.HTTPUnauthorized(
            'Invalid token', 'Provided token is not recognized as valid'
        )


def require_admin(req: Request, resp: Response, resource, params: dict):
    """Request hook that ensures client sent valid admin token.

    :param req: request object
    :type req: Request
    :param resp: response object
    :type resp: Response
    :param resource: resource object serving this request
    :type resource: Any
    :param params: request params
    :type params: dict
    :raises falcon.HTTPUnauthorized: if token is missing or does not match
                                     hardcoded one
    """
    if req.auth != os.environ['ADMIN_TOKEN']:
        raise falcon.HTTPUnauthorized(
            'Admin token required', 'Admin authorization token required'
        )
