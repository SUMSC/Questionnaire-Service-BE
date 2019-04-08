from flask import Flask
from flask_graphql import GraphQLView
from .model import db_session
from .schema import schema
from config import config


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object(config['DEVELOP'])
    else:
        app.config.from_object(config['TESTING'])

    @app.route('/')
    def hello():
        return 'Hello, World!'

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True  # for having the GraphiQL interface
        )
    )

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
