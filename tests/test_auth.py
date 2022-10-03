import unittest
from src import create_app
from src.config.config import config_dict
from src.models import db, User
from flask_jwt_extended import create_access_token

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

    data={
            "username":"testuser",
            "email":"testuser@gmail.com",
            "password":"password"
        }

    def test_user_register(self):
        response=self.client.post('/api/v1/auth/user',json=UserTestCase.data)
        user=User.query.filter_by(email="testuser@gmail.com").first()
        assert user.username == "testuser"
        assert response.status_code == 201


    def test_login(self):
        response=self.client.post('/api/v1/auth/user',json=UserTestCase.data)

        data={
            "email":"testuser@gmail.com",
            "password":"password"
        }
        response=self.client.post('/api/v1/auth/login',json=data)
        assert response.status_code == 200


    def test_buyer_can_deposit_coins(self):
        response=self.client.post('/api/v1/auth/user',json=UserTestCase.data)

        token=create_access_token(identity=1, additional_claims={
                    "roles": ['buyer']
                    })

        headers={
            "Authorization": f"Bearer {token}"
        }
        data={
            "deposit": 5
        }
        response=self.client.post('/api/v1/auth/deposit',json=data, headers=headers)
        assert response.status_code == 200
        user=User.query.filter_by(email="testuser@gmail.com").first()
        assert user.deposit == 5


    def test_seller_cannot_deposit_coins(self):
        response=self.client.post('/api/v1/auth/user',json=UserTestCase.data)

        token=create_access_token(identity=1, additional_claims={
                    "roles": ['seller']
                    })

        headers={
            "Authorization": f"Bearer {token}"
        }
        data={
            "deposit": 5
        }
        response=self.client.post('/api/v1/auth/deposit',json=data, headers=headers)
        assert response.status_code == 403


    def test_buy_with_insufficient_deposit(self):
        response=self.client.post('/api/v1/auth/user',json=UserTestCase.data)
        user=User.query.filter_by(email="testuser@gmail.com").first()

        data={
                "productName": "red bull",
                "cost": 20,
                "amountAvailable": 10
        }
        token=create_access_token(identity=1, additional_claims={
                    "roles": ['seller']
                    })
        headers={
            "Authorization": f"Bearer {token}"
        }
        response=self.client.post('/api/v1/products/',json=data,headers=headers)

        data={
                "productId":1,
                "amount_of_products": 2
        }
        token=create_access_token(identity=1, additional_claims={
                    "roles": [role.name for role in user.roles]
                    })
        headers={
            "Authorization": f"Bearer {token}"
        }
        response=self.client.post('/api/v1/auth/buy',json=data,headers=headers)
        assert response.status_code == 400

    def test_buy_with_deposit(self):
        response=self.client.post('/api/v1/auth/user',json=UserTestCase.data)
        user=User.query.filter_by(email="testuser@gmail.com").first()

        data={
                "productName": "red bull",
                "cost": 20,
                "amountAvailable": 10
        }
        token=create_access_token(identity=1, additional_claims={
                    "roles": ['seller']
                    })
        headers={
            "Authorization": f"Bearer {token}"
        }
        response=self.client.post('/api/v1/products/',json=data,headers=headers)
        token=create_access_token(identity=1, additional_claims={
                    "roles": [role.name for role in user.roles]
                    })
        headers={
            "Authorization": f"Bearer {token}"
        }
        data={
            "deposit": 50
        }
        response=self.client.post('/api/v1/auth/deposit',json=data, headers=headers)

        data={
                "productId":1,
                "amount_of_products": 2
        }
        response=self.client.post('/api/v1/auth/buy',json=data,headers=headers)
        assert response.status_code == 200
        assert response.json['change'] == [10]
        assert response.json['amount_spent'] == 40


    def test_seller_cannot_buy_products(self):
        response=self.client.post('/api/v1/auth/user',json=UserTestCase.data)
        
        data={
                "productName": "red bull",
                "cost": 20,
                "amountAvailable": 10
        }
        token=create_access_token(identity=1, additional_claims={
                    "roles": ['seller']
                    })
        headers={
            "Authorization": f"Bearer {token}"
        }
        response=self.client.post('/api/v1/products/',json=data,headers=headers)

        data={
                "productId":1,
                "amount_of_products": 2
        }
        response=self.client.post('/api/v1/auth/buy',json=data,headers=headers)
        assert response.status_code == 403




