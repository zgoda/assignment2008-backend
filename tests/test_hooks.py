def test_auth_missing(client):
    rv = client.simulate_post('/wallets')
    assert rv.status_code == 401
    assert rv.json['title'] == 'Missing token'


def test_auth_invalid(client):
    rv = client.simulate_post('/wallets', headers={'Authorization': 'wrong-token'})
    assert rv.status_code == 401
    assert rv.json['title'] == 'Invalid token'
