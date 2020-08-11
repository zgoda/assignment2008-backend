import pytest


def test_auth_missing(client):
    rv = client.simulate_post('/wallets')
    assert rv.status_code == 401
    assert rv.json['title'] == 'Missing token'


def test_auth_invalid(client):
    rv = client.simulate_post('/wallets', headers={'Authorization': 'wrong-token'})
    assert rv.status_code == 401
    assert rv.json['title'] == 'Invalid token'


@pytest.mark.parametrize('token', [None, 'invalid'], ids=['none', 'invalid'])
def test_admin_token_wrong(client, token):
    headers = {}
    if token:
        headers['Authorization'] = token
    rv = client.simulate_get('/statistics', headers=headers)
    assert rv.status_code == 401
    assert rv.json['title'] == 'Admin token required'
