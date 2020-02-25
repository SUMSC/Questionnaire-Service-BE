import logging
import json
import time
import re

import yaml
from flask import Blueprint, current_app, redirect, jsonify, request
from resource.models import db
from resource.exceptions import InvalidRequestError


def load_router(file='./router.yaml'):
    with open(file) as router_file:
        return yaml.load(router_file.read())


def check_type(data, except_type):
    if except_type == 'string' or except_type == 'any':
        return True
    if except_type == 'int':
        return str.isdigit(data)
    if except_type in ['list', 'dict', 'bool']:
        try:
            _ = json.loads(data)
        except json.decoder.JSONDecodeError:
            return False
        return isinstance(_, eval(except_type))
    if except_type == 'date':
        try:
            _ = time.strptime(data, '%Y-%m-%d')
        except ValueError:
            return False
        return True


def check_restrain(restrain):
    def distribute_restrain(where):
        place = None
        if where == 'cookies':
            place = request.cookies
        elif where == 'query':
            place = request.args
        elif where == 'json':
            place = request.get_json()
        for r in restrain[where]:
            if place.get(r['name']) is None:
                if r['required']:
                    raise InvalidRequestError(r['name'], where, f"{r['name']} in {where} is required")
                continue
            if not check_type(place.get(r['name']), r.get('type', 'any')):
                raise InvalidRequestError(r['name'], where, f"{r['name']} in {where} has wrong type")

    for i in restrain:
        try:
            distribute_restrain(i)
        except InvalidRequestError:
            raise


def route_match(path):
    def _(route):
        return re.search(route, path) is not None
    return _


def general_error(status_code, message):
    return {
        'code': status_code,
        'message': message
    }


def select_data(model, query):
    """
    Just for qnaire
    :param model:
    :param query:
    :return:
    """
    current_app.logger.debug("SELECT %s %s" % (model, query))
    offset = query.pop('offset', 0)
    sort = query.pop('sort', 'create_time')
    limit = query.pop('limit', 10)
    return jsonify(general_error(200, [
        item.to_dict() for item in
        db.session.query(model).filter_by(**query).order_by(
            getattr(model, sort).desc()
        ).limit(limit).offset(offset).all()
    ])), 200


def create_data(model, data):
    current_app.logger.debug("INSERT %s %s" % (model, data))
    new_field = model(**data)
    db.session.add(new_field)
    try:
        db.session.commit()
    except Exception as e:
        detail = str(e).split('\n')[1]
        return jsonify(general_error(400, detail)), 400
    return jsonify(general_error(201, 'created')), 201


def update_data(model, ids, data):
    current_app.logger.debug("UPDATE %s %s" % (model, data))
    field = db.session.query(model).filter_by(**ids).first()
    if field is None:
        return jsonify(general_error(400, 'cannot found')), 400
    if len(data.items()) == 0:
        return jsonify(general_error(200, 'nothing to update')), 200
    for i in data:
        setattr(field, i, data[i])
    try:
        db.session.commit()
    except Exception as e:
        detail = str(e).split('\n')[1]
        return jsonify(general_error(400, detail)), 400
    else:
        return jsonify(general_error(200, 'ok')), 200


def delete_data(model, data):
    current_app.logger.debug("DELETE %s %s" % (model, data))
    field = db.session.query(model).filter_by(**data).first()
    if field is None:
        return jsonify(general_error(400, 'cannot found')), 400
    db.session.delete(field)
    try:
        db.session.commit()
    except Exception as e:
        detail = str(e).split('\n')[1]
        return jsonify(general_error(400, detail)), 400
    else:
        return jsonify(general_error(204, 'no content')), 204
