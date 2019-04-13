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
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://sumsc:sumsc666@192.168.2.101:55432/eform"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 5
        db.init_app(app)

    app.add_url_rule(
        '/',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True
        )
    )

    return app
