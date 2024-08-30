from db import db


class ExpenseModel(db.Model):
    __tablename__ = "expenses"

    # auto-increment by defult
    id = db.Column(db.Integer, primary_key=True)
    # if we want items with an unique name, than add unique=True
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String())
    amount = db.Column(db.Float(precision=2), unique=False, nullable=False)
    date = db.Column(db.Date(), unique=False, nullable=False)

    receipt_url = db.Column(db.String())
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False
    )

    user = db.relationship("UserModel", back_populates="expenses")
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), unique=False, nullable=False
    )

    category = db.relationship("CategoryModel", back_populates="expenses")
