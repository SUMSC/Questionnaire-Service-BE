import os
from tempfile import TemporaryFile
from datetime import datetime
from time import time

import jwt
from pprint import pprint
from flask import Blueprint, current_app, redirect, jsonify, request, g, send_from_directory
from werkzeug.utils import secure_filename

from resource.exceptions import InvalidRequestError, QnaireParserError
from resource.models import db, User as UserModel, \
    Qnaire as QnaireModel, Answer as AnswerModel
from resource.utils import route_match, check_restrain, general_error, \
    select_data, create_data, update_data, delete_data, load_router, excel_parser

api = Blueprint('auth', __name__, url_prefix='/api')
# CORS(api, resources={r"/*": {"origins": "http://localhost:9527"}})


@api.before_request
def check_router():
    # router = load_router()
    router = {}
    routes = filter(route_match(request.path), router.keys())
    for route in routes:
        print(route)
        restrains = router[route]
        if restrains.get('ALL'):
            try:
                check_restrain(restrains['ALL'])
            except InvalidRequestError as e:
                current_app.logger.error(f"[{e.place}] {e.params} is invalid for {e.message}")
                return jsonify(general_error(400, e.message))
        if restrains.get(request.method):
            try:
                check_restrain(restrains[request.method])
            except InvalidRequestError as e:
                current_app.logger.error(f"[{e.place}] {e.params} is invalid for {e.message}")
                return None


@api.before_request
def check_authorization():
    token = request.cookies.get('AUTHORIZATION')
    if not token:
        token = request.headers.get('X-Custom-Auth')
    if token:
        token_payload = jwt.decode(
            token, current_app.config['SECRET_KEY'],
            options={'verify_exp': True})
        if token_payload:
            g.token_payload = token_payload
        else:
            return jsonify(general_error(401, '登陆已过期')), 401


@api.route('/')
def api_documentation():
    return redirect('https://app.swaggerhub.com/apis-docs/wzhzzmzzy/eForm-API/1.0.0-oas3')


@api.route('/upload', methods=['POST', 'DELETE'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        if file is None or file.filename == '':
            return jsonify(general_error(400, 'no file'))
        if not os.path.exists('upload'):
            os.mkdir('upload')
        today = str(datetime.now()).split()[0]
        now = int(time())
        today_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], today)
        filename = f'{g.token_payload["id"]}_{now}_{secure_filename(file.filename)}'
        if not os.path.exists(today_dir):
            os.mkdir(today_dir)
        file.save(os.path.join(today_dir, filename))
        return jsonify(general_error(200, os.path.join(today_dir, filename)))
    if request.method == 'DELETE':
        file = request.json['file']
        try:
            os.remove(file)
        except Exception as e:
            return jsonify(general_error(400, e))
        else:
            return jsonify(general_error(200, 'ok'))


@api.route('/my/<target>', methods=['GET'])
def my_api(target):
    query = request.args.to_dict()
    query['owner_id'] = g.token_payload['id']
    model = None
    if target == 'qnaire':
        model = QnaireModel
    elif target == 'answer':
        model = AnswerModel
    else:
        return jsonify(general_error(401, 'unknown target')), 401
    page = request.args.get('page', 1)
    sort = query.pop('sort', 'create_time')
    data = db.session.query(model).filter_by(**query).order_by(
        getattr(model, sort).desc()
    ).paginate(page=page, per_page=10)
    # data = model.query.paginate(page=page, per_page=10)
    return jsonify(general_error(200, {
        target: [i.to_dict() for i in data.items],
        'page_num': data.pages
    })), 200


@api.route('/user', methods=['GET', 'POST'])
def user_api():
    model = UserModel
    if request.method == 'GET':
        query = request.args.to_dict()
        if query.get('id_tag'):
            curr = db.session.query(model).filter_by(**query).first()
            if curr is None:
                return jsonify(general_error(400, 'cannot found')), 400
            return jsonify(general_error(200, curr.to_dict()))
        token_payload = g.token_payload
        curr = db.session.query(model).filter_by(id_tag=token_payload['id']).first()
        if curr is None:
            res = create_data(model, {
                'id_tag': token_payload['id'],
                'name': token_payload['name'],
                'type': '学生' if token_payload['usertype'] == '1' else '教师'
            })
            if res[1] == 201:
                curr = db.session.query(model).filter_by(id_tag=token_payload['id']).first()
                return jsonify(general_error(200, curr.to_dict()))
            else:
                return res
        return jsonify(general_error(200, curr.to_dict()))
    if request.method == 'POST':
        return create_data(model, request.json)


@api.route('/qnaire', methods=['GET', 'POST', 'PUT', 'DELETE'])
def qnaire_api():
    # 是否是匿名问卷
    qs = request.args.to_dict()
    model = QnaireModel
    if request.method == 'GET':
        return select_data(model, qs)
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        data = request.get_json()
        return update_data(model, {'id': data.pop('id')}, data)
    if request.method == 'DELETE':
        return delete_data(model, {'id': request.get_json()['id']})


@api.route('/answer', methods=['GET', 'POST', 'PUT'])
def answer_api():
    # is_anonymous = request.args.get('a') == 'true'
    # model = GAnswerModel if is_anonymous else AnswerModel
    model = AnswerModel
    if request.method == 'GET':
        # if is_anonymous:
        #     return jsonify(general_error(400, 'anonymous answer cannot be selected'))
        return select_data(model, request.args.to_dict())
    if request.method == 'POST':
        data = dict(**request.json, owner_id=g.token_payload['id'])
        return create_data(model, data)
    if request.method == 'PUT':
        # if is_anonymous:
        #     return jsonify(general_error(400, 'anonymous answer cannot be updated'))
        data = request.json
        return update_data(model, {'id': data.pop('id')}, data)


@api.route('/import/excel', methods=['POST'])
def qnaire_from_excel():
    print(request.files)
    file = request.files.get('file')
    if file is None or file.filename == '':
        return jsonify(general_error(400, 'no file'))
    try:
        with TemporaryFile() as temp_file:
            temp_file.write(file.stream.read())
            qnaire = excel_parser(temp_file)
    except QnaireParserError as e:
        return jsonify(general_error(400, e.message)), 400
    model = QnaireModel
    qnaire['owner_id'] = g.token_payload['id']
    qnaire['active'] = False
    qnaire['settings'] = {
        'only_once': True,
        'allow_edit': False,
        'shuffle_selections': False
    }
    return create_data(model, qnaire)
