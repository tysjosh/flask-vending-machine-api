import unittest
from src import create_app
from src.config.config import config_dict
from src.models import db, Product
from flask_jwt_extended import create_access_token

class ProductTestCase(unittest.TestCase):

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

    def test_get_all_products(self):
        token = create_access_token(identity=1)

        headers={
            "Authorization":f"Bearer {token}"
        }
        response = self.client.get('/api/v1/products', headers=headers)

        assert response.status_code == 200
        assert response.json == []

    def test_create_product(self):
        data={
                "productName": "red bull",
                "cost": 20,
                "amountAvailable": 10
        }

        token=create_access_token(identity=1)

        headers={
            "Authorization":f"Bearer {token}"
        }

        response=self.client.post('/api/v1/products',json=data,headers=headers)
        assert response.status_code == 201
        products= Product.query.all()
        assert len(products) == 1