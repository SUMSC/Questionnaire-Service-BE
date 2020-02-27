import os

from flask import Flask, request, jsonify, send_from_directory

from werkzeug.utils import secure_filename
# from flask_graphql import GraphQLView

from .models import db
from .restful import api


# from .schema import schema


def create_app(test_conf=None):
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(api)
    if test_conf:
        for i in test_conf:
            app.config[i] = test_conf[i]
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://eform:changeit@wzhzzmzzy.xyz:5432/eform"
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

    @app.route('/build_index')
    def build_index_pg():
        """
        重建 ZomboDB 索引，用于测试
        :return:
        """
        db.session.execute("""
        CREATE INDEX idxqnaire ON qnaire USING zombodb ((qnaire.*)) WITH (url='elasticsearch:9200/', alias='qnaire');
        CREATE INDEX idxevent ON event USING zombodb ((event.*)) WITH (url='elasticsearch:9200/', alias='event');
        """)
        db.session.commit()
        return "build success"

    @app.route('/reindex')
    def reindex_pg():
        """
        Reindex ZomboDB，用于定时脚本访问，清除无效数据
        :return:
        """
        db.session.execute("""
        REINDEX INDEX idxevent;
        REINDEX INDEX idxqnaire;
        """)
        db.session.commit()
        return "success"

    # app.add_url_rule(
    #     '/graphql',
    #     view_func=GraphQLView.as_view(
    #         'graphql',
    #         schema=schema,
    #         graphiql=True
    #     )
    # )

    return app
