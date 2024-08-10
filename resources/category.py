from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from sqlalchemy.exc import SQLAlchemyError
from db import db

from models import CategoryModel
from schemas import CategorySchema

blp = Blueprint("Categories", "categories",
                description="Operations on categories")


@blp.route("/category/<int:categorie_id>")
class Category(MethodView):

    @jwt_required()
    @blp.response(200, CategorySchema)
    def get(self, categorie_id):
        item = CategoryModel.query.get_or_404(categorie_id)
        return item

    @jwt_required(fresh=True)
    def delete(self, categorie_id):
        item = CategoryModel.query.get_or_404(categorie_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}


@blp.route("/category")
class CategoryList(MethodView):

    # many=True return a list of items
    @jwt_required()
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        return CategoryModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(CategorySchema)
    @blp.response(201, CategorySchema)
    def post(self, category_data):

        current_user = get_jwt_identity()
        category = CategoryModel(**category_data, user_id=current_user)
        try:
            db.session.add(category)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback in case of error
            abort(
                500, message=f"An error occurred while inserting the item: {str(e)}")

        return category, 201
