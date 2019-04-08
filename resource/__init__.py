import os
import click

from flask import Flask, request, jsonify
from flask.cli import with_appcontext
from flask_graphql import GraphQLView
from .model import db
from .schema import schema


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.route('/')
    def resource():
        req = request.get_json()
        res = schema.execute(req, context_value={'session': db.session})
        return jsonify(res)

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True  # for having the GraphiQL interface
        )
    )

    return app
