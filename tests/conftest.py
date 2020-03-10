import pytest

from resource import create_app
from resource.models import db


@pytest.fixture
def app():
    app = create_app('TESTING')
    db.init_app(app)
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
