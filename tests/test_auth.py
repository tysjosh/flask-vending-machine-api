import unittest
from src import create_app
from src.config.config import config_dict
from src.models import db, User


class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=config_dict['testing'])
        self.appctx= self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.client = None

    def test_user_register(self):
        data={
            "username":"testuser",
            "email":"testuser@company.com",
            "password":"password"
        }
        response=self.client.post('/api/v1/auth/user',json=data)

        user=User.query.filter_by(email="testuser@company.com").first()
        assert user.username == "testuser"
        assert response.status_code == 201

    def test_login(self):

        data={
            "email":"testuser@gmail.com",
            "password":"password"
        }
        response=self.client.post('/api/v1/auth/login',json=data)
        assert response.status_code == 401
