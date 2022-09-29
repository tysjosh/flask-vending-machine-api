from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# Initialize Flask-SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    deposit = db.Column(db.Integer)
    roles = db.relationship('Role', secondary='user_role', backref="users")
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))
    products = db.relationship('Product', backref="users")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    @classmethod
    def find_by_name(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def get_roles_name(self):
        return [role.name for role in self.roles]

    def get_products_name(self):
        return [product.productName for product in self.products]

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'deposit': self.deposit,
            'roles': self.get_roles_name(),
            'products':self.get_products_name(),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def __repr__(self) -> str:
        return f'<User "{self.username}">'


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f'<Role "{self.name}">'

user_role = db.Table ('user_role',
                    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
                    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'))
                    )

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(80), unique=True, nullable=False)
    cost = db.Column(db.Integer, nullable=True)
    amountAvailable = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

    def to_json(self):
        return {
            'id': self.id,
            'productName': self.productName,
            'cost': self.cost,
            'amountAvailable': self.amountAvailable,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def __repr__(self) -> str:
        return f'<Product "{self.productName}">'

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)