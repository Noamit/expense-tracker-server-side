from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from sqlalchemy.exc import SQLAlchemyError
from db import db

from models import ExpenseModel
from schemas import ExpenseSchema

blp = Blueprint("Expenses", "expenses", description="Operations on expenses")


@blp.route("/expense/<int:expense_id>")
class Expense(MethodView):

    @jwt_required()
    @blp.response(200, ExpenseSchema)
    def get(self, expense_id):
        item = ExpenseModel.query.get_or_404(expense_id)
        return item

    @jwt_required(fresh=True)
    def delete(self, expense_id):
        item = ExpenseModel.query.get_or_404(expense_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}


@blp.route("/expense")
class ExpenseList(MethodView):

    # many=True return a list of items
    @jwt_required()
    @blp.response(200, ExpenseSchema(many=True))
    def get(self):
        current_user = get_jwt_identity()
        return ExpenseModel.query.filter_by(user_id=current_user).all()

    @jwt_required(fresh=True)
    @blp.arguments(ExpenseSchema)
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data):

        current_user = get_jwt_identity()
        expense = ExpenseModel(**expense_data, user_id=current_user)
        try:
            db.session.add(expense)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback in case of error
            abort(
                500, message=f"An error occurred while inserting the item: {str(e)}")

        return expense, 201
