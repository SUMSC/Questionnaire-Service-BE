import pickle

from flask import Flask, request, jsonify, send_from_directory

from config import config
from .models import db
from .restful import api
from .utils import dump_csv_to_db, get_all_area


def create_app(env='DEVELOP'):
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(api)
    app.config.from_object(config[env])
    db.init_app(app)
    with open('resource/static/china_area.pk', 'rb') as pkf:
        china_area = pickle.load(pkf)

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

    @app.route('/files/<filename>')
    def get_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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

    @app.route('/api/china_area')
    def get_china_area():
        return jsonify(china_area)

    return app
