from decimal import Decimal


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
    rv = client.simulate_get(
        f'/wallets/{address1}/transactions', headers={'Authorization': user}
    )
    assert len(rv.json) == 1
    trn_data = rv.json[0]
    assert Decimal(trn_data['fee']) == Decimal(0)
    assert trn_data['from'] == address1
    assert trn_data['to'] == address2
    assert Decimal(trn_data['amount']) == Decimal(data['amount'])
    assert trn_data['type'] == 'OUT'
