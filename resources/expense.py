import os
import math

from datetime import date
from dateutil.relativedelta import relativedelta
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
# from app import app  # Importing the app instance

from flask import jsonify, request, current_app, send_from_directory, url_for
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from sqlalchemy.exc import SQLAlchemyError
from db import db

from models import ExpenseModel
from schemas import ExpenseSchema, ExpenseUpdateSchema

from sqlalchemy import func
from sqlalchemy import text

from calendar import month_name

blp = Blueprint("Expenses", "expenses", description="Operations on expenses")

# Route to serve uploaded files


@blp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


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

    @jwt_required(fresh=True)
    @blp.arguments(ExpenseUpdateSchema, location="form")
    @blp.response(201, ExpenseSchema)
    def put(self, expense_data, expense_id):
        item = ExpenseModel.query.get(expense_id)

        if not item:
            return {"message": "Expense not found"}, 404

        # Update only the fields that are present in expense_data
        if "amount" in expense_data:
            item.amount = expense_data["amount"]
        if "name" in expense_data:
            item.name = expense_data["name"]
        if "description" in expense_data:
            item.description = expense_data.get(
                "description", item.description)
        if "date" in expense_data:
            item.date = expense_data["date"]
        if "category_id" in expense_data:
            item.category_id = expense_data["category_id"]

        receipt_file = request.files.get('receipt')
        if receipt_file:
            filename = secure_filename(receipt_file.filename)
            filepath = os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename)
            # Save the file to the specified directory
            receipt_file.save(filepath)
            receipt_url = url_for(
                'Expenses.uploaded_file', filename=filename, _external=True)

            item.receipt_url = receipt_url

        db.session.commit()
        return item


@blp.route("/expense")
class ExpenseList(MethodView):

    # many=True return a list of items
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        query = ExpenseModel.query.filter_by(user_id=current_user)

        # Get optional query parameters
        name = request.args.get('name')
        category_id = request.args.get('category_id')
        date = request.args.get('date')
        # Page number (default to 1)
        page = request.args.get('page', type=int, default=1)
        per_page = 10  # Number of items per page

        if name:
            query = query.filter(ExpenseModel.name.ilike(f"%{name}%"))
        if category_id:
            query = query.filter(ExpenseModel.category_id == category_id)
        if date:
            query = query.filter(ExpenseModel.date == date)

        total_expenses = query.count()
        total_pages = math.ceil(total_expenses / per_page)

        # Pagination: apply offset and limit
        paginated_query = query.offset((page - 1) * per_page).limit(per_page)
        expenses = paginated_query.all()
        # Serialize the expenses using ExpenseSchema
        expense_schema = ExpenseSchema(many=True)
        expenses_data = expense_schema.dump(expenses)

        # Return the paginated response
        return {
            'expenses': expenses_data,  # List of paginated and serialized expenses
            'total_pages': total_pages,  # Total number of pages
            'current_page': page  # The current page number
        }

    @jwt_required(fresh=True)
    @blp.arguments(ExpenseSchema, location="form")
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data):

        # Get the file from the request
        receipt_file = request.files.get('receipt')
        if receipt_file:
            filename = secure_filename(receipt_file.filename)
            filepath = os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename)
            # Save the file to the specified directory
            receipt_file.save(filepath)
            receipt_url = url_for(
                'Expenses.uploaded_file', filename=filename, _external=True)

            expense_data['receipt_url'] = receipt_url

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


@blp.route("/expense/monthly_totals")
class ExpenseByMonth(MethodView):

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        months_param = request.args.get('months', default=6, type=int)
        # months_param = months_param - 1 if months_param >= 1 else 0

        start_date = date.today() - relativedelta(months=+months_param)
        start_date = start_date.replace(day=1)

        sql_query = text("""
                        SELECT 
                            strftime('%Y-%m', date) AS month, 
                            SUM(amount) AS total_amount
                        FROM expenses
                        WHERE user_id = :user_id 
                        AND date >= :start_date 
                        GROUP BY month
                        ORDER BY month;
                    """)

        # Execute the query
        result = db.session.execute(sql_query, {
            'user_id': current_user,
            'start_date': start_date
        }).fetchall()

        all_months = []
        expenses_dict = {row.month: row.total_amount for row in result}
        current_date = start_date
        end_date = date.today().replace(day=1)

        while current_date <= end_date:
            month_str = current_date.strftime('%Y-%m')
            all_months.append({
                'month': f"{month_name[int(month_str.split('-')[1])]} {month_str.split('-')[0]}",
                # Default to 0 if no expenses
                'amount': expenses_dict.get(month_str, 0)
            })
            current_date += relativedelta(months=1)

        return jsonify(all_months), 200
