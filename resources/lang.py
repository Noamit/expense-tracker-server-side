from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt

from sqlalchemy.exc import SQLAlchemyError
from db import db

from models import LangModel
from schemas import LangSchema, LangUpdateSchema

blp = Blueprint("Langs", "langs",
                description="Operations on langs")


@blp.route("/lang/<int:lang_id>")
class Lang(MethodView):

    @jwt_required()
    @blp.response(200, LangSchema)
    def get(self, lang_id):
        item = LangModel.query.get_or_404(lang_id)
        return item

    @jwt_required(fresh=True)
    def delete(self, lang_id):
        claims = get_jwt()
        if not claims.get('is_admin'):
            abort(403, message="Admin privileges are required to access this resource.")

        item = LangModel.query.get_or_404(lang_id)

        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

    @jwt_required(fresh=True)
    @blp.arguments(LangUpdateSchema)
    @blp.response(200, LangSchema)
    def put(self, lang_data, lang_id):
        claims = get_jwt()
        if not claims.get('is_admin'):
            abort(403, message="Admin privileges are required to access this resource.")

        item = LangModel.query.get_or_404(lang_id)

        if not item:
            return {"message": "Lang not found"}, 404
         # Update only the fields that are present in expense_data
        if "name" in lang_data:
            item.name = lang_data["name"]

        db.session.commit()
        return item


@blp.route("/lang")
class LangList(MethodView):

    @jwt_required()
    @blp.response(200, LangSchema(many=True))
    def get(self):
        claims = get_jwt()
        if not claims.get('is_admin'):
            abort(403, message="Admin privileges are required to access this resource.")
        return LangModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(LangSchema)
    @blp.response(201, LangSchema)
    def post(self, lang_data):

        claims = get_jwt()
        if not claims.get('is_admin'):
            abort(403, message="Admin privileges are required to access this resource.")

        lang = LangModel(**lang_data)
        try:
            db.session.add(lang)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback in case of error
            abort(
                500, message=f"An error occurred while inserting the item: {str(e)}")

        return lang, 201
