import os
import math
import hashlib

from datetime import date
from dateutil.relativedelta import relativedelta
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

from utils import csv_export


blp = Blueprint("Expenses", "expenses", description="Operations on expenses")

# Route to serve uploaded files


@blp.route('/csv_exports/<filename>')
def csv_exports_file(filename):
    return send_from_directory(current_app.config['CSV_EXPORT_FOLDER'], filename)


@blp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


def generate_hashed_filename(expense_id, original_filename):
    """Generate a hashed filename using expense ID and original filename."""
    # Extract the file extension
    file_extension = os.path.splitext(original_filename)[1]
    hash_object = hashlib.sha256(f"{expense_id}_{original_filename}".encode())
    return f"{hash_object.hexdigest()}{file_extension}"


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

        current_user = get_jwt_identity()
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
            original_filename = secure_filename(receipt_file.filename)
            filename = generate_hashed_filename(expense_id, original_filename)
            filepath = os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename)
            # Save the file to the specified directory
            receipt_file.save(filepath)
            receipt_url = url_for(
                'Expenses.uploaded_file', filename=filename, _external=True)

            item.receipt_url = receipt_url
        else:
            item.receipt_url = None
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
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export = request.args.get('export', type=int, default=0)
        # Page number (default to 1)
        page = request.args.get('page', type=int, default=1)
        per_page = 10  # Number of items per page
        export_url = ''

        if name:
            query = query.filter(ExpenseModel.name.ilike(f"%{name}%"))
        if category_id:
            query = query.filter(ExpenseModel.category_id == category_id)
        if start_date:
            query = query.filter(ExpenseModel.date >= start_date)
        if end_date:
            query = query.filter(ExpenseModel.date <= end_date)

        total_expenses = query.count()

        total_pages = 1 if total_expenses == 0 else math.ceil(
            total_expenses / per_page)

        if not export:
            # Pagination: apply offset and limit
            query = query.offset((page - 1) * per_page).limit(per_page)

        expenses = query.all()

        # Serialize the expenses using ExpenseSchema
        expense_schema = ExpenseSchema(many=True)
        expenses_data = expense_schema.dump(expenses)

        if export:
            expenses_data_for_export = []

            for expense in expenses_data:
                new_expense = {}
                new_expense["name"] = expense["name"]
                new_expense["description"] = expense["description"]
                new_expense["category"] = expense["category"]["name"]
                new_expense["amount"] = expense["amount"]
                new_expense["date"] = expense["date"]

                expenses_data_for_export.append(new_expense)

            filename = csv_export(user_id=current_user, headers=[
                "name", "description", "category", "amount", "date"], data=expenses_data_for_export)
            export_url = url_for(
                'Expenses.csv_exports_file', filename=filename, _external=True)
        # Return the paginated response
        return {
            'expenses': expenses_data,
            'total_pages': total_pages,
            'current_page': page,
            'export_url': export_url
        }

    @jwt_required(fresh=True)
    @blp.arguments(ExpenseSchema, location="form")
    @blp.response(201, ExpenseSchema)
    def post(self, expense_data):

        current_user = get_jwt_identity()
        # Get the file from the request

        expense = ExpenseModel(**expense_data, user_id=current_user)
        try:
            db.session.add(expense)
            db.session.commit()

            receipt_file = request.files.get('receipt')
            if receipt_file:
                original_filename = secure_filename(receipt_file.filename)
                filename = generate_hashed_filename(
                    expense.id, original_filename)
                filepath = os.path.join(
                    current_app.config['UPLOAD_FOLDER'], filename)
                # Save the file to the specified directory
                receipt_file.save(filepath)
                receipt_url = url_for(
                    'Expenses.uploaded_file', filename=filename, _external=True)

                expense.receipt_url = receipt_url
                db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback in case of error
            abort(
                500, message=f"An error occurred while inserting the item: {str(e)}")

        return expense, 201
