import os

from flask import Flask, request, jsonify, send_from_directory
from flask_graphql import GraphQLView
from flask_cors import CORS
from werkzeug.utils import secure_filename
from .models import db
from .schema import schema


def create_app(test_conf=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r"/": {"origins": "*"}})
    if test_conf:
        for i in test_conf:
            app.config[i] = test_conf[i]
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://sumsc:sumsc666@192.168.2.101:55432/eform"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 5
        app.config['UPLOAD_FOLDER'] = "upload"
        db.init_app(app)

    @app.route('/upload', methods=['POST'])
    def upload_file():
        print(request.files)
        file = request.files.get('file')
        if file is None or file.filename == '':
            return jsonify({"ok": False, "detail": "no file"})
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"ok": True, "detail": filename})

    @app.route('/files/<filename>')
    def get_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    app.add_url_rule(
        '/',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True
        )
    )

    return app
