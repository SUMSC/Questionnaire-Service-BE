import jwt
from flask import Blueprint, current_app, redirect, jsonify, request
from flask_cors import CORS

from resource.exceptions import InvalidRequestError
from resource.models import db, User as UserModel, \
    Qnaire as QnaireModel, GAnswer as GAnswerModel, \
    Answer as AnswerModel, Anaire as AnaireModel
from resource.utils import route_match, check_restrain, general_error, \
    select_data, create_data, update_data, delete_data, load_router

api = Blueprint('auth', __name__, url_prefix='/api')
CORS(api)


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


@api.route('/')
def api_documentation():
    # return redirect('https://app.swaggerhub.com/apis-docs/wzhzzmzzy/eForm-API/1.0.0-oas3')
    return 'ok'


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
        token_payload = jwt.decode(request.cookies['X-Access-Token'])
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
    if request.method == 'POST':
        return create_data(model, request.json)


@api.route('/qnaire', methods=['GET', 'POST', 'PUT', 'DELETE'])
def qnaire_api():
    # 是否是匿名问卷
    model = AnaireModel if request.args.get('a') == 'true' else QnaireModel
    if request.method == 'GET':
        return select_data(model, request.args.to_dict())
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        data = request.get_json()
        return update_data(model, {'id': data.pop('id')}, data)
    if request.method == 'DELETE':
        return delete_data(model, {'id': request.get_json()['id']})


@api.route('/answer', methods=['GET', 'POST', 'PUT'])
def answer_api():
    is_anonymous = request.args.get('a') == 'true'
    model = GAnswerModel if is_anonymous else AnswerModel
    if request.method == 'GET':
        if is_anonymous:
            return jsonify(general_error(400, 'anonymous answer cannot be selected'))
        return select_data(model, request.args.to_dict())
    if request.method == 'POST':
        return create_data(model, request.json)
    if request.method == 'PUT':
        if is_anonymous:
            return jsonify(general_error(400, 'anonymous answer cannot be updated'))
        data = request.json
        return update_data(model, {'id': request.get_json()['id']}, data)
