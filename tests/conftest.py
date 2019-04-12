import pytest

from resource import create_app
from resource.models import db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "mysql+mysqldb://root:sumsc666@wzhzzmzzy.xyz:33306/eform",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })
    db.init_app(app)

    yield app

    with app.app_context():
        db.drop_all()
        db.create_all()


@pytest.fixture
def client(app):
    return app.test_client()
