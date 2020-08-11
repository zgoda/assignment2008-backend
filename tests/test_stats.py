from decimal import Decimal


def test_read_no_fees(client, wallet):
    address1, user = wallet
    rv = client.simulate_post('/wallets', headers={'Authorization': user})
    address2 = rv.json['address']
    data = {
        'from': address1,
        'to': address2,
        'amount': 1000000,
    }
    client.simulate_post(
        '/transactions', headers={'Authorization': user}, json=data
    )
    admin_token = 'admin'
    rv = client.simulate_get('/statistics', headers={'Authorization': admin_token})
    assert rv.json['transactions'] == 1
    assert Decimal(rv.json['profit']) == Decimal(0)


def test_read_with_profit(client, wallet):
    address1, user1 = wallet
    rv = client.simulate_post('/users')
    user2 = rv.json['token']
    rv = client.simulate_post('/wallets', headers={'Authorization': user2})
    address2 = rv.json['address']
    data = {
        'from': address1,
        'to': address2,
        'amount': 1000000,
    }
    client.simulate_post(
        '/transactions', headers={'Authorization': user1}, json=data
    )
    admin_token = 'admin'
    rv = client.simulate_get('/statistics', headers={'Authorization': admin_token})
    assert rv.json['transactions'] == 1
    assert Decimal(rv.json['profit']) == Decimal(1000000) * Decimal('0.015')
