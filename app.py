from flask import Flask, jsonify
from flask_cors import CORS
from db import db
from dotenv import load_dotenv
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

import models

from resources.user import blp as UserBlueprint
from resources.expense import blp as ExpenseBlueprint
from resources.category import blp as CategoryBlueprint


def create_app(db_url=None):

    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Expense Tracker REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # will create a file called data.db.
    # if there is db_url it will connect to the uel and if not it will conect to the env variable by sqlite
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config['UPLOAD_FOLDER'] = "uploads"
    # init SQLALCHEMY with our flack app
    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)
    CORS(app)
    # todo: create a new key and remove from code
    app.config["JWT_SECRET_KEY"] = "76517074903035659443580166051695395839"
    jwt = JWTManager(app)

    api.register_blueprint(ExpenseBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(CategoryBlueprint)
    return app
