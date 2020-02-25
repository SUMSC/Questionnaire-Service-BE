# import functools
# import re
#
# from flask import Blueprint, g, request, jsonify, current_app, redirect
# from flask_cors import CORS
#
# from sqlalchemy.exc import IntegrityError
# from resource.exceptions import InvalidRequestError
# from resource.models import db, User as UserModel, \
#     Qnaire as QnaireModel, GAnswer as GAnswerModel, \
#     Answer as AnswerModel, Anaire as AnaireModel
#
#
# # api = Blueprint('auth', __name__, url_prefix='/api')
# # CORS(api)
# #
# #
# # @api.before_request
# # def check_request():
# #     routes = filter(route_match(request.path), router.keys())
# #     for route in routes:
# #         print(route)
# #         restrains = router[route]
# #         if restrains.get('ALL'):
# #             try:
# #                 check_restrain(restrains['ALL'])
# #             except InvalidRequestError as e:
# #                 return None
# #         if restrains.get(request.method):
# #             try:
# #                 check_restrain(restrains[request.method])
# #             except InvalidRequestError as e:
# #                 return None
#
#
# @api.route('/')
# def api_doc():
#     return 'ok'
#
#
# @api.route('/user', methods=['GET', 'POST'])
# def user_api():
#     model = UserModel
#     if request.method == 'GET':
#         query = dict(list(request.args.items()))
#         curr = db.session.query(model).filter_by(**query).first()
#         if curr is None:
#             return jsonify(general_error(400, 'cannot found')), 400
#         return jsonify(general_error(200, curr.to_dict()))
#     if request.method == 'POST':
#         return create_data(model, request.json)
#     # if request.method == 'PUT':
#     #     data = request.json
#     #     if data.get('id') is None:
#     #         return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
#     #     return update_data(model, {'id': data.pop('id')}, data)
#
#
# # @api.route('/event', methods=['GET', 'POST', 'PUT', 'DELETE'])
# # def event_api():
# #     model = EventModel
# #     if request.method == 'GET':
# #         return select_data(model, dict(list(request.args.items())))
# #     if request.method == 'POST':
# #         return create_data(model, request.json)
# #     if request.method == 'PUT':
# #         data = request.json
# #         if data.get('id') is None:
# #             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
# #         return update_data(model, {'id': data.pop('id')}, data)
# #     if request.method == 'DELETE':
# #         data = request.json
# #         if data.get('id') is None:
# #             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
# #         return delete_data(model, {'id': data['id']})
#
#
# @api.route('/anaire', methods=['GET', 'POST', 'PUT', 'DELETE'])
# def anaire_api():
#     model = AnaireModel
#     if request.method == 'GET':
#         return select_data(model, dict(list(request.args.items())))
#     if request.method == 'POST':
#         return create_data(model, request.json)
#     if request.method == 'PUT':
#         data = request.json
#         if data.get('id') is None:
#             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
#         return update_data(model, {'id': data.pop('id')}, data)
#     if request.method == 'DELETE':
#         data = request.json
#         if data.get('id') is None:
#             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
#         return delete_data(model, {'id': data['id']})
#
#
# # @api.route('/participate', methods=['GET', 'POST', 'PUT', 'DELETE'])
# # def paricipate_api():
# #     model = ParticipateModel
# #     if request.method == 'GET':
# #         return select_data(model, dict(list(request.args.items())))
# #     if request.method == 'POST':
# #         return create_data(model, request.json)
# #     if request.method == 'PUT':
# #         data = request.json
# #         if data.get('user_id') is None or data.get('event_id') is None:
# #             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
# #         return update_data(model, {'user_id': data.pop('user_id'), 'event_id': data.pop('event_id')}, data)
# #     if request.method == 'DELETE':
# #         data = request.json
# #         if data.get('user_id') is None or data.get('event_id') is None:
# #             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
# #         return delete_data(model, {'user_id': data['user_id'], 'event_id': data['event_id']})
#
#
# @api.route('/answer', methods=['GET', 'POST', 'PUT', 'DELETE'])
# def answer_api():
#     model = AnswerModel
#     if request.method == 'GET':
#         return select_data(model, dict(list(request.args.items())))
#     if request.method == 'POST':
#         return create_data(model, request.json)
#     if request.method == 'PUT':
#         data = request.json
#         if data.get('user_id') is None or data.get('qnaire_id') is None:
#             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
#         return update_data(model, {'user_id': data.pop('user_id'), 'qnaire_id': data.pop('qnaire_id')}, data)
#     if request.method == 'DELETE':
#         data = request.json
#         if data.get('user_id') is None or data.get('qnaire_id') is None:
#             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
#         return delete_data(model, {'user_id': data['user_id'], 'qnaire_id': data['qnaire_id']})
#
#
# @api.route('/anonymous_answer', methods=['GET', 'POST', 'PUT', 'DELETE'])
# def anonymous_answer_api():
#     model = AnonymousAnswerModel
#     if request.method == 'GET':
#         return select_data(model, dict(list(request.args.items())))
#     if request.method == 'POST':
#         return create_data(model, request.json)
#     if request.method == 'PUT':
#         data = request.json
#         if data.get('qnaire_id') is None:
#             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
#         return update_data(model, {'qnaire_id': data.pop('qnaire_id')}, data)
#     if request.method == 'DELETE':
#         data = request.json
#         if data.get('qnaire_id') is None:
#             return jsonify({'ok': False, 'data': {"error": "no id"}}), 400
#         return delete_data(model, {'qnaire_id': data['qnaire_id']})
