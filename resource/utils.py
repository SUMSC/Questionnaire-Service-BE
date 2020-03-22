import logging
import json
import time
import re
import os
import functools
from copy import deepcopy
from datetime import datetime

import yaml
import tablib
import requests
from pprint import pprint
from concurrent import futures
from flask import current_app, jsonify, request
from resource.models import db, ChinaArea
from resource.exceptions import InvalidRequestError, QnaireParserError

question_type = {
    '文本描述': 'plain-text',
    '单选题': 'qnaire-select',
    '多选题': 'qnaire-checkbox',
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
    sort = query.pop('sort', 'create_time')
    desc = query.pop('desc', False)
    result = [
        item.to_dict() for item in
        db.session.query(model).filter_by(**query).order_by(
            getattr(model, sort).desc() if desc else getattr(model, sort)
        ).all()
    ]
    if len(result) > 0:
        return jsonify(general_error(200, result)), 200
    else:
        return jsonify(general_error(404, 'not found')), 404


def create_data(model, data):
    current_app.logger.debug("INSERT %s %s" % (model, data))
    new_field = model(**data)
    db.session.add(new_field)
    try:
        db.session.commit()
    except Exception as e:
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
        if i == 'deadline':
            data[i] = datetime.strptime(data[i], "%a %b %d %Y %H:%M:%S %Z%z")
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
    qnaire_data['a'] = qnaire_type == '匿名问卷'
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
                form_data['meta']['selection'] = tuple(filter(lambda x: x, meta))
            if form_data['type'] == '日期选择题':
                if meta[0] and re.match(date_pattern, meta[0].strftime('%Y-%m-%d')) is not None:
                    form_data['meta']['form'] = meta[0].strftime('%Y-%m-%d')
                if meta[1] and re.match(date_pattern, meta[1].strftime('%Y-%m-%d')) is not None:
                    form_data['meta']['to'] = meta[1].strftime('%Y-%m-%d')
        try:
            form_data['type'] = question_type[form_data['type']]
        except KeyError as e:
            raise QnaireParserError(f'未知的题目类型：{e.args[0]}')
        qnaire_data['form'].append(form_data)
    return qnaire_data


def get_area(page=1, level=0):
    host = 'https://api02.aliyun.venuscn.com'
    path = '/area/all'
    app_code = 'f4dbe38260f24ddea262a96c2b6eb40c'
    url = host + path
    qs = {
        'level': level,
        'page': page,
        'size': 50,
    }
    headers = {
        'Authorization': 'APPCODE ' + app_code
    }
    response = requests.get(url, params=qs, headers=headers)
    data = response.json()['data']
    return data


def get_city_by_parent(parent_id):
    host = 'https://api02.aliyun.venuscn.com'
    path = '/area/query'
    app_code = 'f4dbe38260f24ddea262a96c2b6eb40c'
    url = host + path
    headers = {
        'Authorization': 'APPCODE ' + app_code
    }
    qs = {
        'parent_id': parent_id
    }
    response = requests.get(url, params=qs, headers=headers)
    data = response.json()['data']
    return data


def dump_area(base_dir, name, depth=1):
    if depth == 0:
        return
    parent_json = os.path.join(base_dir, f'{name}.json')
    print(f'Loading areas from {parent_json}')
    with open(parent_json, 'r', encoding='utf8') as f:
        areas = json.load(f)
        for area in areas:
            area_dir = os.path.join(base_dir, area["pinyin"])
            area_json = os.path.join(area_dir, f'{area["pinyin"]}.json')
            if not os.path.exists(area_dir):
                os.mkdir(area_dir)
                cities = get_city_by_parent(area['id'])
                with open(area_json, 'w', encoding='utf8') as city_f:
                    print(f'Dumping areas to {area_json}')
                    json.dump(cities, city_f)
            dump_area(area_dir, area['pinyin'], depth=depth-1)


def dump_province_to_csv():
    provinces = get_area()
    provinces_data = tablib.Dataset(headers=provinces[0].keys())
    for i in provinces:
        provinces_data.append(i.values())
    print(provinces_data.export('csv'))
    with open('static/provinces.csv', 'w', encoding='gbk', newline='\n') as csv_f:
        csv_f.write(provinces_data.export('csv'))


def dump_city_to_csv(level=1, from_page=1, max_page=15, step=10):
    get_city = functools.partial(get_area, level=level)
    page_one = get_city(from_page)
    city_data = tablib.Dataset(headers=page_one[0].keys())
    for city in page_one:
        city_data.append(city.values())
    last_page = max_page
    if max_page < 50:
        with futures.ProcessPoolExecutor(max_workers=6) as executor:
            res = executor.map(get_city, range(from_page+1, max_page))
        res = tuple(res)
        for page in res:
            for city in page:
                city_data.append(city.values())
    else:
        for i in range(from_page+1, max_page, step):
            if i % 50 < 10:
                print('Now:', i)
            with futures.ProcessPoolExecutor(max_workers=6) as executor:
                res = executor.map(get_city, range(i, i+step))
            res = tuple(res)
            exit_flag = False
            for page in res:
                if len(page) == 0:
                    last_page = i + step
                    exit_flag = True
                    break
                for city in page:
                    city_data.append(city.values())
            if exit_flag:
                print('End:', last_page)
                break
    with open(f'static/city_{level}_{from_page}_{last_page}.csv', 'w', encoding='gbk', newline='\n') as csv_f:
        csv_f.write(city_data.export('csv'))


def remove_redundancy(csv_path):
    with open(csv_path, 'w+', encoding='gbk', newline='\n') as f:
        csv_data = tablib.Dataset().load(f, format='csv')
        csv_data.remove_duplicates()
        f.write(csv_data.export('csv'))


def dump_csv_to_db(csv_path):
    with open(csv_path, 'r', encoding='gbk', newline='\n') as f:
        csv_data = tablib.Dataset().load(f, format='csv')
        for i in csv_data:
            new_field = ChinaArea(**i)
            db.session.add(new_field)
        db.session.commit()


def get_all_area():
    areas = db.session.query(ChinaArea).filter(ChinaArea.level < 3).all()
    counties = {i.id: dict(value=i.pinyin, label=i.name, pid=i.parent_id) for i in areas if i.level == 2}
    cities = {i.id: dict(value=i.pinyin, label=i.name, pid=i.parent_id, children=[]) for i in areas if i.level == 1}
    provinces = {i.id: dict(value=i.pinyin, label=i.name, children=[]) for i in areas if i.level == 0}
    del areas
    for county in counties.values():
        cities[county['pid']]['children'].append(dict(label=county['label'], value=county['value']))
    del counties
    for city in cities.values():
        provinces[city['pid']]['children'].append(dict(
            label=city['label'],
            value=city['value'],
            children=deepcopy(city['children'])))
    del cities
    return provinces


if __name__ == '__main__':
    # with open('static/qnaire_excel_test.xlsx', 'rb') as f:
    #     pprint(excel_parser(f))
    # dump_area('static/china_administrative_divisions', 'provinces', depth=4)
    pass
