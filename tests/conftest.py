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

    db.create_all(app=app)
    yield app

    db.session.execute("drop table anonymous_answer")
    db.session.execute("drop table answer")
    db.session.execute("drop table participate")
    db.session.execute("drop table event")
    db.session.execute("drop table qnaire")
    db.session.execute("drop table user")

# TODO: Fix this fixture
