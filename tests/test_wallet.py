from decimal import Decimal

from pony.orm import db_session, select

from backend.models import Wallet


def test_create(client, user, mocker):
    rate = Decimal('12345.67') / Decimal(100000000)
    mocker.patch('backend.models.get_rate', mocker.Mock(return_value=rate))
    rv = client.simulate_post('/wallets', headers={'Authorization': user})
    assert rv.json['address']
    assert rv.json['balance']['BTC'] == float(Decimal(1))
    assert rv.json['balance']['USD'] == float(rate * Decimal(100000000))
    with db_session:
        select(
            w.balance for w in Wallet if w.address == rv.json['address']
        ).first() == 100000000


def test_create_not_allowed(client, user, mocker):
    rate = Decimal('12345.67') / Decimal(100000000)
    mocker.patch('backend.models.get_rate', mocker.Mock(return_value=rate))
    for _ in range(10):
        client.simulate_post('/wallets', headers={'Authorization': user})
    rv = client.simulate_post('/wallets', headers={'Authorization': user})
    assert rv.status_code == 403


def test_read(client, wallet, mocker):
    address, user = wallet
    rate = Decimal('12345.67') / Decimal(100000000)
    mocker.patch('backend.models.get_rate', mocker.Mock(return_value=rate))
    rv = client.simulate_get(f'/wallets/{address}', headers={'Authorization': user})
    assert rv.json['address']
    assert rv.json['balance']['BTC'] == float(Decimal(1))
    assert rv.json['balance']['USD'] == float(rate * Decimal(100000000))


def test_read_not_found(client, wallet, mocker):
    address, user = wallet
    rv = client.simulate_get('/wallets/does-not-exist', headers={'Authorization': user})
    assert rv.status_code == 404
