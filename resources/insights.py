from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from db import db

from sqlalchemy import text
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from calendar import month_name

blp = Blueprint("Insights", "insights",
                description="Operations on insights")


@blp.route("/monthly_totals")
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
                'month': f"{month_name[int(month_str.split('-')[1])]}",
                'year': f"{month_str.split('-')[0]}",
                # Default to 0 if no expenses
                'amount': expenses_dict.get(month_str, 0)
            })
            current_date += relativedelta(months=1)

        return jsonify(all_months), 200


@blp.route("/category_totals")
class ExpenseByCategory(MethodView):

    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()

        # current_month = str(datetime.now().month)
        current_month = str(datetime.now().month)
        current_month = str(current_month).rjust(2, '0')

        current_year = str(datetime.now().year)
        sql_query = text("""
                            SELECT 
                                categories.name AS name,
                                SUM(expenses.amount) AS value 
                            FROM expenses 
                            INNER JOIN categories ON 
                            expenses.category_id = categories.id 
                            WHERE 
                                expenses.user_id = :user_id 
                                AND strftime('%m', expenses.date) = :month 
                                AND strftime('%Y', expenses.date) = :year 
                            GROUP BY categories.id;
                        """)

        # Execute the query
        result = db.session.execute(
            sql_query,
            {"user_id": current_user, "month": current_month, "year": current_year}
        ).fetchall()

        result_list = [{"name": row.name, "value": row.value}
                       for row in result]

        return result_list, 200
