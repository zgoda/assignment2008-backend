from decimal import Decimal

from pony.orm import db_session, select

from backend.models import Wallet


def test_create_own_accounts(client, wallet):
    address1, user = wallet
    rv = client.simulate_post('/wallets', headers={'Authorization': user})
    address2 = rv.json['address']
    data = {
        'from': address1,
        'to': address2,
        'amount': 1000000,
    }
    rv = client.simulate_post(
        '/transactions', headers={'Authorization': user}, json=data
    )
    assert rv.status_code == 201
    with db_session:
        w1 = select(w for w in Wallet if w.address == address1).first()
        w2 = select(w for w in Wallet if w.address == address2).first()
        assert w1.balance + w2.balance == Decimal(200000000)
        assert w2.balance == Decimal(101000000)


def test_read(client, wallet):
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
    rv = client.simulate_get('/transactions', headers={'Authorization': user})
    trn_data = rv.json[0]
    assert Decimal(trn_data['fee']) == Decimal(0)
    assert trn_data['from'] == address1
    assert trn_data['to'] == address2
    assert Decimal(trn_data['amount']) == Decimal(data['amount'])


def test_create_different_users(client, wallet):
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
    rv = client.simulate_post(
        '/transactions', headers={'Authorization': user1}, json=data
    )
    assert rv.status_code == 201
    with db_session:
        w1 = select(w for w in Wallet if w.address == address1).first()
        w2 = select(w for w in Wallet if w.address == address2).first()
        assert w1.balance + w2.balance != Decimal(200000000)
        assert w2.balance == Decimal(101000000)
        assert w1.balance == Decimal(99000000) - Decimal(1000000) * Decimal('0.015')


def test_create_wallet_not_found(client, wallet):
    address1, user1 = wallet
    address2 = 'non-existing'
    data = {
        'from': address1,
        'to': address2,
        'amount': 1000000,
    }
    rv = client.simulate_post(
        '/transactions', headers={'Authorization': user1}, json=data
    )
    assert rv.status_code == 400
    assert rv.json['error']['code'] == 'WALLET_NOT_FOUND'


def test_create_own_wallet_not_found(client, wallet):
    _, user1 = wallet
    address1 = 'non-existing-1'
    address2 = 'non-existing-2'
    data = {
        'from': address1,
        'to': address2,
        'amount': 1000000,
    }
    rv = client.simulate_post(
        '/transactions', headers={'Authorization': user1}, json=data
    )
    assert rv.status_code == 400
    assert rv.json['error']['code'] == 'WALLET_NOT_FOUND'
    assert 'or is not yours' in rv.json['error']['message']


def test_create_not_enough_funds(client, wallet):
    address1, user = wallet
    rv = client.simulate_post('/wallets', headers={'Authorization': user})
    address2 = rv.json['address']
    data = {
        'from': address1,
        'to': address2,
        'amount': 100000001,
    }
    rv = client.simulate_post(
        '/transactions', headers={'Authorization': user}, json=data
    )
    assert rv.status_code == 400
    assert rv.json['error']['code'] == 'NOT_ENOUGH_FUNDS'
