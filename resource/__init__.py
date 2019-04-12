import os

from flask import Flask, request, jsonify
from flask_graphql import GraphQLView
from .models import db
from .schema import schema


def create_app(test_conf=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_conf:
        for i in test_conf:
            app.config[i] = test_conf[i]
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqldb://root:sumsc666@wzhzzmzzy.xyz:33306/eform"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 5
        db.init_app(app)

    @app.route('/', methods=['POST'])
    def resource():
        req = request.get_json()
        query = req['query']
        variables = req['variables']
        res = schema.execute(query, variables=variables, context={'session': db.session})
        return jsonify(res.data)

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True  # for having the GraphiQL interface
        )
    )

    return app
