from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from db import db

from models import TranslateModel, LangModel
from schemas import TranslateSchema, GeneralDeclarationSchema
from utils import get_default_lang_id

blp = Blueprint("GeneralDeclaration", "generalDeclaration",
                description="Operations on generalDeclaration")


@blp.route("/Gd")
class generalDeclaration(MethodView):

    @blp.response(200, GeneralDeclarationSchema())
    def get(self):
        # Replace with your logic to get the default language
        lang_id = request.args.get('lang_id') or get_default_lang_id()
        translations = TranslateModel.query.filter_by(lang_id=lang_id).all()
        langs = LangModel.query.all()
        langs_dict = {l.id: l.name for l in langs}
        translations_dict = {t.key: t.value for t in translations}

        # Return the general declaration with default language and translations
        result = {
            "lang_id": lang_id,
            "translations": translations_dict,
            "langs": langs_dict
        }

        return result
