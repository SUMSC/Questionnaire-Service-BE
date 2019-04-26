import functools

from flask import Blueprint, g, request, jsonify
from sqlalchemy.exc import IntegrityError
from .models import db, Event as EventModel, User as UserModel, \
    Participate as ParticipateModel, Qnaire as QnaireModel, AnonymousAnswer as AnonymousAnswerModel, \
    Answer as AnswerModel, AnonymousQnaire as AnonymousQnaireModel

api = Blueprint('auth', __name__, url_prefix='/api')


def select_data(model, query):
    """
    Just for event / qnaire
    :param model:
    :param data:
    :return:
    """
    offset = query.pop('offset', 10)
    sort = query.pop('sort', 'create_time')
    limit = query.pop('limit', 0)
    return {'ok': True, 'data': [item.to_dict() for item in
                                 db.session.query(model)
                                     .filter_by(**query)
                                     .limit(limit)
                                     .offset(offset)
                                     .order_by(getattr(model, sort).desc())
                                     .all()
                                 ]
            }, 200


def create_data(model, data):
    new_field = model(**data)
    db.session.add(new_field)
    try:
        db.session.commit()
    except Exception as e:
        detail = str(e).split('\n')[1]
        return jsonify({'ok': False, 'data': {"error": detail}}), 400
    return jsonify({'ok': True, 'data': new_field.to_dict()}), 201


def updata_data(model, data):
    if data.get(id) is None:
        return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
    field = db.session.query(model).filter_by(id=data['id']).first()
    if field is None:
        return jsonify({'ok': False, 'data': {"error": "cannot found"}}), 400
    if len(list(filter(lambda x: x[1] is not None, data.items()))) == 0:
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
    if data.get(id) is None:
        return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
    field = db.session.query(model).filter_by(id=data['id']).first()
    if field is None:
        return jsonify({'ok': False, 'data': {"error": "cannot found"}}), 400
    db.session.delete(field)
    try:
        db.session.commit()
    except Exception as e:
        detail = str(e).split('\n')[1]
        return jsonify({'ok': False, 'data': {"error": detail}}), 400
    else:
        return jsonify({'ok': True, 'data': field.to_dict()}), 200


@api.route('/user', methods=['GET', 'POST', 'PUT'])
def user_api():
    model = UserModel
    if request.method == 'GET':
        query = dict(list(request.args.items()))
        return jsonify(db.session.query(model).filter_by(**query).first().to_dict())
    if request.method == 'POST':
        return create_data(model, dict(list(request.json)))
    if request.method == 'PUT':
        return updata_data(model, dict(list(request.json)))


@api.route('/event', methods=['GET', 'POST', 'PUT', 'DELETE'])
def event_api():
    model = EventModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, dict(list(request.json)))
    if request.method == 'PUT':
        return updata_data(model, dict(list(request.json)))
    if request.method == 'DELETE':
        return updata_data(model, dict(list(request.json)))


@api.route('/qnaire', methods=['GET', 'POST', 'PUT', 'DELETE'])
def qnaire_api():
    model = QnaireModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, dict(list(request.json)))
    if request.method == 'PUT':
        return updata_data(model, dict(list(request.json)))
    if request.method == 'DELETE':
        return updata_data(model, dict(list(request.json)))


@api.route('/anonymous_qnaire', methods=['GET', 'POST', 'PUT', 'DELETE'])
def anonymous_qnaire_api():
    model = AnonymousQnaireModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, dict(list(request.json)))
    if request.method == 'PUT':
        return updata_data(model, dict(list(request.json)))
    if request.method == 'DELETE':
        return updata_data(model, dict(list(request.json)))


@api.route('/participate', methods=['GET', 'POST', 'PUT', 'DELETE'])
def paricipate_api():
    model = ParticipateModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, dict(list(request.json)))
    if request.method == 'PUT':
        return updata_data(model, dict(list(request.json)))
    if request.method == 'DELETE':
        return updata_data(model, dict(list(request.json)))


@api.route('/answer', methods=['GET', 'POST', 'PUT', 'DELETE'])
def answer_api():
    model = AnswerModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, dict(list(request.json)))
    if request.method == 'PUT':
        return updata_data(model, dict(list(request.json)))
    if request.method == 'DELETE':
        return updata_data(model, dict(list(request.json)))


@api.route('/anonymous_answer', methods=['GET', 'POST', 'PUT', 'DELETE'])
def anonymous_answer_api():
    model = AnonymousAnswerModel
    if request.method == 'GET':
        return select_data(model, dict(list(request.args.items())))
    if request.method == 'POST':
        return create_data(model, dict(list(request.json)))
    if request.method == 'PUT':
        return updata_data(model, dict(list(request.json)))
    if request.method == 'DELETE':
        return updata_data(model, dict(list(request.json)))
