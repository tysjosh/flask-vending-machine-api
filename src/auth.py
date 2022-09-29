from crypt import methods
from functools import wraps
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, \
    HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, \
    get_jwt_identity, verify_jwt_in_request, get_jwt, unset_jwt_cookies
from flasgger import swag_from
from src.models import Product, User, Role, TokenBlocklist, db
from datetime import datetime, timezone
from src.extensions import jwt


auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
COINS = [5, 10, 20, 50, 100]


def buyer_required():
    """
        Here is a custom decorator that verifies the JWT is present in the request,
        as well as insuring that the JWT has a claim indicating that this user is
        a buyer
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if "buyer" in claims["roles"]:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Buyer only!"), 403
        return decorator
    return wrapper


@auth.post('/login')
@swag_from('./docs/auth/login.yml')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:
        roles = [role.name for role in user.roles]
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id, 
                additional_claims={
                    "roles": roles
                    }
                )

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'roles': roles
                }

            }), HTTP_200_OK

    return jsonify({'error': 'User with credentials not found'}), HTTP_401_UNAUTHORIZED


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    return jsonify({
        'access': access
    }), HTTP_200_OK


@auth.delete('/logout')
@jwt_required(verify_type=False)   
def logout():
    """
        endpoint where the frontend can send a DELETE for each token
    """
    try:
        token = get_jwt()
        jti = token["jti"]
        ttype = token["type"]
        now = datetime.now()
        db.session.add(TokenBlocklist(jti=jti, type=ttype, created_at=now))
        db.session.commit()
        return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")
    except Exception:
        return {'error': "there was a problem revoking this token"}




# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    """
        This function is called whenever a valid JWT is used to access a protected route. 
        The callback will receive the JWT header and JWT payload as arguments, 
        and must return True if the JWT has been revoked.
    """
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify(user.to_json()), HTTP_200_OK


@auth.post('/user')
@swag_from('./docs/auth/register.yml')
def register():
    
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    roles = request.json.get('roles', ['buyer'])
    deposit = request.json.get('deposit', 0)

    if len(password) < 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': "User is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT
    
    pwd_hash = generate_password_hash(password)
    user = User(username=username, password=pwd_hash, email=email)
    user.deposit = deposit
    for role_name in roles:
        db_role = Role.query.filter_by(name=role_name).first()
        if db_role:
            user.roles.append(db_role)
        else:
            user.roles.append(Role(name=role_name))
    user.save_to_db()

    return jsonify({
        'message': "User created",
        'user': {
            'username': username,
             "email": email,
             "roles": roles
        }

    }), HTTP_201_CREATED


@auth.post("/deposit")
@buyer_required()
def deposit_coins():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    
    deposit = request.json.get("deposit")
    if deposit not in COINS:
        return jsonify({'error': "You can only deposit 5, 10, 20, 50 and 100 cent coin"}), HTTP_400_BAD_REQUEST
    if user.deposit is None:
        user.deposit = 0
    user.deposit = user.deposit + deposit
    db.session.commit()
    return jsonify(user.to_json()), HTTP_200_OK


@auth.post("/buy")
@buyer_required()
def buy_product():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    
    productId = request.json.get("productId")
    amount_of_products = request.json.get("amount_of_products")
    product = Product.query.get(productId)
    change = []
    amount_remaining = user.deposit
    product_cost = product.cost
    number_product_left = product.amountAvailable

    if amount_of_products > number_product_left:
        return jsonify({'error': "Not enough products available to buy"}), HTTP_400_BAD_REQUEST
    total_cost = amount_of_products * product_cost
    if  total_cost > amount_remaining:
        return jsonify({'error': "Not enough funds to buy all products"}), HTTP_400_BAD_REQUEST

    amount_remaining = amount_remaining - total_cost
    user.deposit = amount_remaining
    number_product_left = number_product_left - amount_of_products
    product.amountAvailable = number_product_left

    while amount_remaining >= COINS[0]:
        if amount_remaining >= COINS[4]:
            amount_remaining = amount_remaining - COINS[4]
            change.append(100)
            continue
        elif amount_remaining >= COINS[3]:
            amount_remaining = amount_remaining - COINS[3]
            change.append(50)
            continue
        elif amount_remaining >= COINS[2]:
            amount_remaining = amount_remaining - COINS[2]
            change.append(20)
            continue
        elif amount_remaining >= COINS[1]:
            amount_remaining = amount_remaining - COINS[1]
            change.append(10)
            continue
        elif amount_remaining >= COINS[0]:
            amount_remaining = amount_remaining - COINS[0]
            change.append(5)
            continue
        else:
            break
    
    db.session.commit()
    return jsonify({
        'productName': product.productName,
        'amount_spent': total_cost,
        'change': change
    }), HTTP_200_OK


@auth.get("/reset")
@buyer_required()
def reset_deposit():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    user.deposit = 0
    db.session.commit()
    return jsonify(user.to_json()), HTTP_200_OK


@auth.get("/user")
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([user.to_json() for user in users])


@auth.delete("/user/<int:id>")
@jwt_required()
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'message': 'User not found'}), HTTP_404_NOT_FOUND
    user.delete_from_db()
    return jsonify({'result': "Deleted"})


@auth.put('/user/<int:id>')
@jwt_required()
def update_user(id):
    if not request.json:
        return jsonify({'error': "No feild provided"}), HTTP_400_BAD_REQUEST

    user = User.query.get(id)
    if user is None:
        return jsonify({'message': 'User not found'}), HTTP_404_NOT_FOUND

    user.username = request.json.get('username', user.username)
    user.email = request.json.get('email', user.email)
    user.deposit = request.json.get('deposit', user.deposit)
    roles = request.json.get('roles', user.roles)

    if roles is not user.roles:
        for role_name in roles:
            db_role = Role.query.filter_by(name=role_name).first()
            if db_role:
                if db_role not in user.roles:
                    user.roles.append(db_role)
            else:
                user.roles.append(Role(name=role_name))

    db.session.commit()
    return jsonify(user.to_json())

@auth.post('user/roles')
@jwt_required()
def assign_roles():
    roles = request.json.get('roles')
    user_id = request.json.get('user_id')

    for role_name in roles:
        if role_name != "buyer" and role_name != "seller":
            return jsonify({'error': "Role must be a seller or buyer"}), HTTP_400_BAD_REQUEST

    user = User.query.get(user_id)
    keep_roles_name = []
    for role_name in roles:
        db_role = Role.query.filter_by(name=role_name).first()
        if db_role:
            user.roles.append(db_role)
            keep_roles_name.append(role_name)
        else:
            user.roles.append(Role(name=role_name))
    db.session.commit()
    return jsonify({
        'message': "Role assigned",
        'roles': {
            'name': keep_roles_name,
        }

    }), HTTP_201_CREATED