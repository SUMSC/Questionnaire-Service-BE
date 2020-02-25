import pytest

from resource import create_app
from resource.models import db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg2://eform:changeit@wzhzzmzzy.xyz:5432/eform",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })
    db.init_app(app)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
