from flask import Flask, jsonify
from src.models import db, TokenBlocklist
from src.auth import auth
from src.products import products
from src.config.swagger import template, swagger_config
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.config.config import config_dict

def create_app(test_config=None, config=config_dict['dev']):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object(config)
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    jwt = JWTManager(app)
    app.register_blueprint(auth)
    app.register_blueprint(products)

    Swagger(app, config=swagger_config, template=template)

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

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR

    return app