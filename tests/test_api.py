import pytest
import json
from flask import request
from resource.models import db

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
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

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
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

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_select_user(client):
    res = client.get(
        '/api/user?id=1'
    )
    res = res.json
    assert res['ok']

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
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

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
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

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_select_event(client):
    res = client.get(
        '/api/event?id=1'
    )
    assert res.status_code == 200
    assert res.json['ok']

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
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

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_create_participate(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read()))
    res = client.post(
        '/api/participate',
        json={
            'user_id': 1,
            'event_id': 1,
            'answer': answer
        }
    )
    assert res.status_code == 201


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_participate(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read()))
    res = client.put(
        '/api/participate',
        json={
            'user_id': 1,
            'event_id': 1,
            'answer': answer
        }
    )
    assert res.status_code == 200


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_create_qnaire(client):
    with open("tests/test_form.json", encoding='utf8') as f:
        form = json.dumps(json.loads(f.read()))
    res = client.post(
        '/api/qnaire',
        json={
            'id': 1,
            'creator_id': 1,
            'name': 'test',
            'deadline': '2019-04-27 17:33:40.913886',
            'form': form,
            'detail': 'test'

        }
    )
    assert res.status_code == 201


def test_create_second_qnaire(client):
    with open("tests/test_form.json", encoding='utf8') as f:
        form = json.dumps(json.loads(f.read()))
    res = client.post(
        '/api/qnaire',
        json={
            'id': 2,
            'creator_id': 2,
            'name': 'test',
            'deadline': '2019-04-27 17:33:40.913886',
            'form': form,
            'detail': 'test'

        }
    )
    assert res.status_code == 201



@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_create_anonymous_qnaire(client):
    with open("tests/test_form.json", encoding='utf8') as f:
        form = json.dumps(json.loads(f.read()))
    res = client.post(
        '/api/anonymous_qnaire',
        json={
            'id': 1,
            'creator_id': 1,
            'name': 'test',
            'deadline': '2019-04-27 17:33:40.913886',
            'form': form,
            'detail': 'test'

        }
    )
    assert res.status_code == 201


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_select_qnaire(client):
    res = client.get(
        '/api/qnaire?id=1'
    )
    assert res.status_code == 200
    assert res.json['ok']


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_select_anonymous_qnaire(client):
    res = client.get(
        '/api/anonymous_qnaire?id=1'
    )
    assert res.status_code == 200
    assert res.json['ok']


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_qnaire(client):
    with open("tests/test_form.json", encoding='utf8') as f:
        form = json.dumps(json.loads(f.read()))
    res = client.put(
        '/api/qnaire',
        json={
            'user_id': 1,
            'id': 1,
            'form': form
        }
    )
    assert res.status_code == 200


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_anonymous_qnaire(client):
    with open("tests/test_form.json", encoding='utf8') as f:
        form = json.dumps(json.loads(f.read()))
    res = client.put(
        '/api/anonymous_qnaire',
        json={
            'user_id': 1,
            'id': 1,
            'form': form
        }
    )
    assert res.status_code == 200


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_create_answer(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read()))
    res = client.post(
        '/api/answer',
        json={
            'user_id': 1,
            'qnaire_id': 1,
            'answer': answer
        }
    )
    assert res.status_code == 201


def test_create_anonymous_answer(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read()))
    res = client.post(
        '/api/anonymous_answer',
        json={
            'qnaire_id': 1,
            'answer': answer
        }
    )
    assert res.status_code == 201


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_select_answer_user_id(client):
    res = client.get(
        '/api/answer?user_id=1'
    )
    assert res.status_code == 200
    assert res.json['ok']


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_select_answer_qnaire_id(client):
    res = client.get(
        '/api/answer?qnaire_id=1'
    )
    assert res.status_code == 200
    assert res.json['ok']


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_select_answer(client):
    res = client.get(
        '/api/answer?qnaire_id=1&user_id=1'
    )
    assert res.status_code == 200
    assert res.json['ok']


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_select_anonymous_answer(client):
    res = client.get(
        '/api/anonymous_answer?qnaire_id=1'
    )
    assert res.status_code == 200
    assert res.json['ok']


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_answer(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read()))
    res = client.put(
        '/api/answer',
        json={
            'user_id': 1,
            'qnaire_id': 1,
            'event_id': 1,
            'answer': answer
        }
    )
    assert res.status_code == 200



@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_anonymous_answer(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read()))
    res = client.put(
        '/api/anonymous_answer',
        json={
            'qnaire_id': 1,
            'event_id': 1,
            'answer': answer
        }
    )
    assert res.status_code == 200


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_delete_answer(client):
    res = client.delete(
        '/api/answer',
        json={
            'user_id': 1,
            'qnaire_id': 1
        }
    )
    assert res.status_code == 204


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_delete_anonymous_answer(client):
    res = client.delete(
        '/api/anonymous_answer',
        json={
            'qnaire_id': 1
        }
    )
    assert res.status_code == 204


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_delete_qnaire(client):
    res = client.delete(
        '/api/qnaire',
        json={
            'id': 1
        }
    )
    assert res.status_code == 204


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_delete_anonymous_qnaire(client):
    res = client.delete(
        '/api/anonymous_qnaire',
        json={
            'id': 1
        }
    )
    assert res.status_code == 204


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_delete_participate(client):
    with open("tests/test_answer.json", encoding='utf8') as f:
        answer = json.dumps(json.loads(f.read()))
    res = client.delete(
        '/api/participate',
        json={
            'user_id': 1,
            'event_id': 1
        }
    )
    assert res.status_code == 204




@pytest.mark.filterwarnings("ignore::DeprecationWarning")
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


