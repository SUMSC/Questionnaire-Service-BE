import pytest
import json
from flask import request
from resource.models import db


def test_create_user(client):
    res = client.post(
        '/api/user',
        json={
            'id_tag': '123456',
            'name': '测试用户'
        }
    )
    assert res.status_code == 201
    res = res.json
    assert res['ok']


def test_create_second_user(client):
    res = client.post(
        '/api/user',
        json={
            'id_tag': '123457',
            'name': '测试用户2'
        }
    )
    res = res.json
    assert res['ok']


def test_select_user(client):
    res = client.get(
        '/api/user?id=1'
    )
    res = res.json
    assert res['ok']


def test_update_user(client):
    res = client.put(
        '/api/user',
        json={
            'id_tag': 123456
        }
    )
    assert res.status_code == 400
    res = client.put(
        '/api/user',
        json={
            'id': 1
        }
    )
    assert res.status_code == 200
    assert res.json['data']['error'] == 'nothing to update'


def test_create_event(client):
    with open("tests/test_form.json", encoding='utf8') as f:
        form = json.dumps(json.loads(f.read()))
    res = client.post(
        '/api/event',
        json={
            'name': "测试活动",
            'detail': "测试数据",
            'deadline': "2004-05-03T17:30:08+08:00",
            'creator_id': 2,
            'form': form,
            'start_time': "2004-05-03T17:30:08+08:00"
        }
    )
    assert res.status_code == 201
    assert res.json['ok']


def test_select_event(client):
    res = client.get(
        '/api/event?id=1'
    )
    assert res.status_code == 200
    assert res.json['ok']


def test_update_event(client):
    res = client.put(
        '/api/event',
        json={
            'id': 1,
            'deadline': "2019-05-03T17:30:08+08:00"
        }
    )
    assert res.status_code == 200
    assert res.json['ok']


def test_create_participate(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read())).replace('"', '\\"')
    res = client.post(
        '/api/participate',
        json={
            'user_id': 1,
            'event_id': 1,
            'answer': answer
        }
    )
    assert res.status_code == 201


def test_update_participate(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read())).replace('"', '\\"')
    res = client.put(
        '/api/participate',
        json={
            'user_id': 1,
            'event_id': 1,
            'answer': answer
        }
    )
    assert res.status_code == 200


def test_delete_participate(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read())).replace('"', '\\"')
    res = client.delete(
        '/api/participate',
        json={
            'user_id': 1,
            'event_id': 1
        }
    )
    assert res.status_code == 204


def test_delete_event(client):
    res = client.delete(
        '/api/event',
        json={
            'id': 1
        }
    )
    assert res.status_code == 204


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_clear(app):
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
