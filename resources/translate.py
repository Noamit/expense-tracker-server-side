from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt

from sqlalchemy.exc import SQLAlchemyError
from db import db

from models import TranslateModel
from schemas import TranslateSchema, TranslateUpdateSchema

blp = Blueprint("Translates", "translates",
                description="Operations on translates")


@blp.route("/translate/<int:translate_id>")
class Translate(MethodView):

    @jwt_required()
    @blp.response(200, TranslateSchema)
    def get(self, translate_id):
        item = TranslateModel.query.get_or_404(translate_id)
        return item

    @jwt_required(fresh=True)
    def delete(self, translate_id):
        claims = get_jwt()
        if not claims.get('is_admin'):
            abort(403, message="Admin privileges are required to access this resource.")

        item = TranslateModel.query.get_or_404(translate_id)

        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

    @jwt_required()
    @blp.arguments(TranslateUpdateSchema)
    @blp.response(200, TranslateSchema)
    def put(self, translate_data, translate_id):
        claims = get_jwt()
        if not claims.get('is_admin'):
            abort(403, message="Admin privileges are required to access this resource.")

        item = TranslateModel.query.get_or_404(translate_id)

        if not item:
            return {"message": "Translate not found"}, 404
         # Update only the fields that are present in expense_data
        if "value" in translate_data:
            item.value = translate_data["value"]
        if "lang_id" in translate_data:
            item.lang_id = translate_data["lang_id"]

        db.session.commit()
        return item


@blp.route("/translate")
class TranslateList(MethodView):

    @jwt_required()
    @blp.response(200, TranslateSchema(many=True))
    def get(self):
        claims = get_jwt()
        if not claims.get('is_admin'):
            abort(403, message="Admin privileges are required to access this resource.")
        return TranslateModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(TranslateSchema)
    @blp.response(201, TranslateSchema)
    def post(self, translate_data):
        claims = get_jwt()
        if not claims.get('is_admin'):
            abort(403, message="Admin privileges are required to access this resource.")

        translate = TranslateModel(**translate_data)
        try:
            db.session.add(translate)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback in case of error
            abort(
                500, message=f"An error occurred while inserting the item: {str(e)}")

        return translate, 201
