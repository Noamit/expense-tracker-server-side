from db import db


class CategoryModel(db.Model):
    __tablename__ = "categories"

    # auto-increment by defult
    id = db.Column(db.Integer, primary_key=True)
    # if we want items with an unique name, than add unique=True
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String())
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False
    )

    user = db.relationship("UserModel", back_populates="categories")
    # expenses = db.relationship(
    #     "ExpenseModel", back_populates="category", lazy="dynamic", cascade="all, delete")
