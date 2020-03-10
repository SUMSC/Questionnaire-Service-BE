import logging
import json
import time
import re

import yaml
import tablib
from pprint import pprint
from flask import Blueprint, current_app, redirect, jsonify, request
from resource.models import db
from resource.exceptions import InvalidRequestError, QnaireParserError

question_type = {
    '文本描述': 'plain-text',
    '单项选择题': 'qnaire-select',
    '多项选择题': 'qnaire-checkbox',
    '单行文本题': 'qnaire-input',
    '多行文本题': 'qnaire-textarea',
    '地域选择题': 'area-picker',
    '日期选择题': 'date-picker',
    '附件题': 'file-uploader'
}


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
        print(str(e))
        detail = str(e).split('\n')[1]
        return jsonify(general_error(400, detail)), 400
    if getattr(new_field, 'id', None):
        return jsonify(general_error(201, new_field.id)), 201
    else:
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


def excel_parser(fd):
    """
    @param fd: The input stream for the uploaded file. This usually points to an open temporary file.
    @return (qnaire: dict, qnaire_type: str)
    """
    date_pattern = re.compile(r'((^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(10|12|0?[13578])([-\/\._])(3[01]|[12]['
                              r'0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(11|0?[469])([-\/\._])(30|['
                              r'12][0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(0?2)([-\/\._])(2[0-8]|1['
                              r'0-9]|0?[1-9])$)|(^([2468][048]00)([-\/\._])(0?2)([-\/\._])(29)$)|(^([3579][26]00)(['
                              r'-\/\._])(0?2)([-\/\._])(29)$)|(^([1][89][0][48])([-\/\._])(0?2)([-\/\._])(29)$)|(^(['
                              r'2-9][0-9][0][48])([-\/\._])(0?2)([-\/\._])(29)$)|(^([1][89][2468][048])([-\/\._])('
                              r'0?2)([-\/\._])(29)$)|(^([2-9][0-9][2468][048])([-\/\._])(0?2)([-\/\._])(29)$)|(^([1]['
                              r'89][13579][26])([-\/\._])(0?2)([-\/\._])(29)$)|(^([2-9][0-9][13579][26])([-\/\._])('
                              r'0?2)([-\/\._])(29)$))')
    qnaire_data = {'form': []}
    qnaire = tablib.Dataset()
    qnaire.load(fd, format='xlsx')
    headers = qnaire.headers
    qnaire_type = qnaire.get_col(0)[0].strip()
    if qnaire_type not in ('实名问卷', '匿名问卷'):
        raise QnaireParserError('unknown type of qnaire')
    qnaire_data['name'] = headers[0].strip()
    qnaire_data['description'] = qnaire.get_col(0)[1].strip()
    if len(qnaire_data['name']) > 30:
        raise QnaireParserError('qnaire name is too long')
    question_names = headers[1:]
    for i, n in enumerate(question_names):
        form_data = {}
        match = re.match(r'\[(.*?)\](.*)', n)
        form_data['id'] = i
        form_data['type'] = match.group(1).strip()
        if form_data['type'] not in ('单行文本题', '多行文本题', '单选题', '多选题', '地域选择题', '日期选择题', '附件题', '文本描述'):
            raise QnaireParserError(f'unknown type of question {i}')
        form_data['name'] = match.group(2).strip()
        if len(form_data['name']) > 100:
            raise QnaireParserError(f'question {i}\'s name is too long')
        if form_data['type'] in ('单选题', '多选题', '日期选择题'):
            meta = qnaire.get_col(i + 1)
            form_data['meta'] = {}
            if form_data['type'] in ('单选题', '多选题'):
                form_data['meta']['selection'] = meta
            if form_data['type'] == '日期选择题':
                if meta[0] and re.match(date_pattern, meta[0].strftime('%Y-%m-%d')) is not None:
                    form_data['meta']['form'] = meta[0].strftime('%Y-%m-%d')
                if meta[1] and re.match(date_pattern, meta[1].strftime('%Y-%m-%d')) is not None:
                    form_data['meta']['to'] = meta[1].strftime('%Y-%m-%d')
        form_data['type'] = question_type[form_data['type']]
        qnaire_data['form'].append(form_data)
    return qnaire_data, qnaire_type


if __name__ == '__main__':
    with open('static/qnaire_excel_test.xlsx', 'rb') as f:
        pprint(excel_parser(f))
