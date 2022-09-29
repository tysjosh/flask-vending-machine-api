from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, \
    HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request, get_jwt
from src.models import Product, db
from flasgger import swag_from
from functools import wraps

products = Blueprint("products", __name__, url_prefix="/api/v1/products")

def seller_required():
    """
        Here is a custom decorator that verifies the JWT is present in the request,
        as well as insuring that the JWT has a claim indicating that this user is
        a seller
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if "seller" in claims["roles"]:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Seller only!"), 403
        return decorator
    return wrapper


@products.route('/', methods=['POST'])
@seller_required()
@swag_from('./docs/products/add_product.yml')
def post_products():
    current_user = get_jwt_identity()

    amountAvailable = request.get_json().get('amountAvailable', None)
    cost = request.get_json().get('cost', None)
    productName = request.get_json().get('productName', '')

    if not validators.length(productName, min=1):
        return jsonify({
            'error': 'Enter a valid product name'
        }), HTTP_400_BAD_REQUEST

    if cost < 0 or cost % 5 != 0:
        return jsonify({
            'error': 'Cost must be multiples of 5 and not less than zero'
        }), HTTP_400_BAD_REQUEST

    if amountAvailable < 0 or amountAvailable==None:
        return jsonify({
            'error': 'Enter a valid amountAvailable, must not be less than zero'
        }), HTTP_400_BAD_REQUEST


    if Product.query.filter_by(productName=productName).first():
        return jsonify({
            'error': 'Product name already exists'
        }), HTTP_409_CONFLICT

    product = Product(productName=productName, cost=cost,
        amountAvailable=amountAvailable, user_id=current_user)
    db.session.add(product)
    db.session.commit()

    return jsonify(product.to_json()), HTTP_201_CREATED


@products.get("/<int:id>")
@jwt_required()
def get_product(id):
    product = Product.query.filter_by(id=id).first()
    if not product:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify(product.to_json()), HTTP_200_OK


@products.route('/', methods=['GET'])
@jwt_required()
@swag_from('./docs/products/add_product.yml')
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    products = Product.query.order_by(Product.id
        ).paginate(page=page, per_page=per_page)

    data = []

    for product in products.items:
        data.append(product.to_json())

    meta = {
        "page": products.page,
        'pages': products.pages,
        'total_count': products.total,
        'prev_page': products.prev_num,
        'next_page': products.next_num,
        'has_next': products.has_next,
        'has_prev': products.has_prev,
    }

    return jsonify({'data': data, "meta": meta}), HTTP_200_OK

@products.delete("/<int:id>")
@seller_required()
def delete_product(id):
    current_user = get_jwt_identity()

    product = Product.query.filter_by(user_id=current_user, id=id).first()
    if not product:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    db.session.delete(product)
    db.session.commit()

    return jsonify({{'result': "Deleted"}}), HTTP_204_NO_CONTENT


@products.put('/<int:id>')
@products.patch('/<int:id>')
@seller_required()
def edit_product(id):
    current_user = get_jwt_identity()

    product = Product.query.filter_by(user_id=current_user, id=id).first()
    if not product:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    product.amountAvailable = request.get_json().get('amountAvailable', product.amountAvailable)
    product.productName = request.get_json().get('productName', product.productName)
    product.cost = request.get_json().get('cost', product.cost)

    db.session.commit()

    return jsonify(product.to_json()), HTTP_200_OK