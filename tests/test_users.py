from pony.orm import db_session

from backend.models import User


def test_create(client):
    with db_session:
        assert User.select().count() == 0
    rv = client.simulate_post('/users')
    assert rv.json['token']
    assert rv.status_code == 201
    with db_session:
        assert User.select().count() == 1


def test_unsupported_method(client):
    rv = client.simulate_get('/users')
    assert rv.status_code == 405
