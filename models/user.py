from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    lang_id = db.Column(
        db.Integer, db.ForeignKey("langs.id"), unique=False, nullable=False
    )
    expenses = db.relationship(
        "ExpenseModel", back_populates="user", lazy="dynamic", cascade="all, delete")
    categories = db.relationship(
        "CategoryModel", back_populates="user", lazy="dynamic", cascade="all, delete")
