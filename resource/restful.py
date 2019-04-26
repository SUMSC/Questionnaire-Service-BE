import functools

from flask import Blueprint, g, request, jsonify, render_template, current_app
from flask_cors import CORS

from sqlalchemy.exc import IntegrityError
from .models import db, Event as EventModel, User as UserModel, \
    Participate as ParticipateModel, Qnaire as QnaireModel, AnonymousAnswer as AnonymousAnswerModel, \
    Answer as AnswerModel, AnonymousQnaire as AnonymousQnaireModel

api = Blueprint('auth', __name__, url_prefix='/api')
CORS(api)


def select_data(model, query):
    """
    Just for event / qnaire
    :param model:
    :param data:
    :return:
    """
    current_app.logger.debug("SELECT %s %s" % (model, query))
    offset = query.pop('offset', 0)
    sort = query.pop('sort', 'create_time')
    limit = query.pop('limit', 10)
    return jsonify({'ok': True,
                    'data': [
                        item.to_dict() for item in
                        db.session.query(model).filter_by(**query).order_by(
                            getattr(model, sort).desc()
                        ).limit(limit).offset(offset).all()
                    ]}), 200


def create_data(model, data):
    current_app.logger.debug("INSERT %s %s" % (model, data))
    new_field = model(**data)
    db.session.add(new_field)
    try:
        db.session.commit()
    except Exception as e:
        detail = str(e).split('\n')[1]
        return jsonify({'ok': False, 'data': {"error": detail}}), 400
    return jsonify({'ok': True, 'data': new_field.to_dict()}), 201


def update_data(model, ids, data):
    current_app.logger.debug("UPDATE %s %s" % (model, data))
    field = db.session.query(model).filter_by(**ids).first()
    if field is None:
        return jsonify({'ok': False, 'data': {"error": "cannot found"}}), 400
    if len(data.items()) == 0:
        return jsonify({'ok': True, 'data': {"error": "nothing to update"}}), 200
    for i in data:
        setattr(field, i, data[i])
    try:
        db.session.commit()
    except Exception as e:
        detail = str(e).split('\n')[1]
        return jsonify({'ok': False, 'data': {"error": detail}}), 400
    else:
        return jsonify({'ok': True, 'data': field.to_dict()}), 200


def delete_data(model, data):
    current_app.logger.debug("DELETE %s %s" % (model, data))
    field = db.session.query(model).filter_by(**data).first()
    if field is None:
        return jsonify({'ok': False, 'data': {"error": "cannot found"}}), 400
    db.session.delete(field)
    try:
        db.session.commit()
    except Exception as e:
        detail = str(e).split('\n')[1]
        return jsonify({'ok': False, 'data': {"error": detail}}), 400
    else:
        return jsonify({'ok': True, 'data': field.to_dict()}), 204


# TODO: 给出 API 文档的网页
@api.route('/')
def api_doc():
    return


@api.route('/user', methods=['GET', 'POST', 'PUT'])
def user_api():
    model = UserModel
    if request.method == 'GET':
        query = dict(list(request.args.items()))
        curr = db.session.query(model).filter_by(**query).first()
        if curr is None:
            return jsonify({'ok': False, "data": "cannot found"}), 400
        return jsonify({'ok': True, "data": curr.to_dict()})
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        data = request.json
        if data.get('id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return update_data(model, {'id': data.pop('id')}, data)


@api.route('/event', methods=['GET', 'POST', 'PUT', 'DELETE'])
def event_api():
    model = EventModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        data = request.json
        if data.get('id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return update_data(model, {'id': data.pop('id')}, data)
    if request.method == 'DELETE':
        data = request.json
        if data.get('id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return delete_data(model, {'id': data['id']})


@api.route('/qnaire', methods=['GET', 'POST', 'PUT', 'DELETE'])
def qnaire_api():
    model = QnaireModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        data = request.json
        if data.get('id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return update_data(model, {'id': data.pop('id')}, data)
    if request.method == 'DELETE':
        data = request.json
        if data.get('id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return delete_data(model, {'id': data['id']})


@api.route('/anonymous_qnaire', methods=['GET', 'POST', 'PUT', 'DELETE'])
def anonymous_qnaire_api():
    model = AnonymousQnaireModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        data = request.json
        if data.get('id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return update_data(model, {'id': data.pop('id')}, data)
    if request.method == 'DELETE':
        data = request.json
        if data.get('id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return delete_data(model, {'id': data['id']})


@api.route('/participate', methods=['GET', 'POST', 'PUT', 'DELETE'])
def paricipate_api():
    model = ParticipateModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        data = request.json
        if data.get('user_id') is None or data.get('event_id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return update_data(model, {'user_id': data.pop('user_id'), 'event_id': data.pop('event_id')}, data)
    if request.method == 'DELETE':
        data = request.json
        if data.get('user_id') is None or data.get('event_id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return delete_data(model, {'user_id': data['user_id'], 'event_id': data['event_id']})


@api.route('/answer', methods=['GET', 'POST', 'PUT', 'DELETE'])
def answer_api():
    model = AnswerModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        data = request.json
        if data.get('user_id') is None or data.get('event_id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return update_data(model, {'user_id': data.pop('user_id'), 'qnaire_id': data.pop('qnaire_id')}, data)
    if request.method == 'DELETE':
        data = request.json
        if data.get('user_id') is None or data.get('qnaire_id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return delete_data(model, {'user_id': data['user_id'], 'qnaire_id': data['qnaire_id']})


@api.route('/anonymous_answer', methods=['GET', 'POST', 'PUT', 'DELETE'])
def anonymous_answer_api():
    model = AnonymousAnswerModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        data = request.json
        if data.get('user_id') is None or data.get('event_id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return update_data(model, {'user_id': data.pop('user_id'), 'qnaire_id': data.pop('qnaire_id')}, data)
    if request.method == 'DELETE':
        data = request.json
        if data.get('user_id') is None or data.get('qnaire_id') is None:
            return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
        return delete_data(model, {'user_id': data['user_id'], 'qnaire_id': data['qnaire_id']})
