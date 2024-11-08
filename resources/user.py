from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from db import db

from models import UserModel
from schemas import UserSchema, UserUpdateSchema, UserPasswordUpdateSchema

blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):

        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]))
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(400, message=str(e),)
        return {"message": "User created successfully."}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):

        user = UserModel.query.filter(
            UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, additional_claims={
                                               'is_admin': user.is_admin}, fresh=True)
            refresh_token = create_refresh_token(identity=user.id, additional_claims={
                                                 'is_admin': user.is_admin})
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials.")


@blp.route("/settings")
class UserSettings(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(UserUpdateSchema)
    @blp.response(201, UserUpdateSchema)
    def put(self, user_data):
        current_user = get_jwt_identity()
        user = UserModel.query.get(current_user)

        if not user:
            abort(401, message="Invalid credentials.")

        # Update only the fields that are present in expense_data
        if "lang_id" in user_data:
            user.lang_id = user_data["lang_id"]

        db.session.commit()
        return user


@blp.route("/user")
class UserPassword(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(UserPasswordUpdateSchema)
    @blp.response(
        202,
        description="not updated",
        example={"message": "Passwords do not match."},
    )
    @blp.response(
        200,
        description="updated",
        example={"message": "Tag deleted."},
    )
    def put(self, user_data):
        current_user = get_jwt_identity()
        user = UserModel.query.get(current_user)

        if user:
            if pbkdf2_sha256.verify(user_data["current_password"], user.password):
                if user_data["new_password"] == user_data["confirm_password"]:
                    user.password = pbkdf2_sha256.hash(
                        user_data["new_password"])
                else:
                    return {"message": "Passwords do not match."}, 202
            else:
                return {"message": "Incorrect password."}, 202
        else:
            abort(401, message="Invalid credentials.")

        db.session.commit()
        return {"message": "Password updated"}, 200
