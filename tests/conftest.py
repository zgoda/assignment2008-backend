import os

import psycopg2
import pytest
import responses
from falcon.testing import TestClient

from backend.app import app
from backend.models import db


@pytest.fixture(autouse=True)
def _setup_env(monkeypatch):
    monkeypatch.setenv('PHGOST', '127.0.0.1')
    monkeypatch.setenv('PGDATABASE', 'test')
    monkeypatch.setenv('PGUSER', 'test')
    monkeypatch.setenv('PGPASSWORD', 'test')


@pytest.fixture()
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture()
def client():
    conn_kw = dict(
        user=os.getenv('PGUSER'), host=os.getenv('PGHOST'),
        dbname='postgres', password=os.getenv('PGPASSWORD'),
    )
    cn = psycopg2.connect(**conn_kw)
    cn.autocommit = True
    cr = cn.cursor()
    cr.execute('drop database if exists test')
    cr.execute('create database test')
    cn.close()
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    yield TestClient(app)
    db.drop_all_tables(with_all_data=True)
    db.disconnect()
    cn = psycopg2.connect(**conn_kw)
    cn.autocommit = True
    cr = cn.cursor()
    cr.execute('drop database test')
    cn.close()


@pytest.fixture()
def user(client):
    rv = client.simulate_post('/users')
    return rv.json['token']


@pytest.fixture()
def wallet(client, user):
    rv = client.simulate_post('/wallets', headers={'Authorization': user})
    return rv.json['address'], user
