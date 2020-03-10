import math

import pytest
import json
from flask import request
from resource.models import db


def test_clear(app):
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
