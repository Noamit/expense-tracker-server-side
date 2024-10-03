from db import db


class LangModel(db.Model):
    __tablename__ = "langs"

    # auto-increment by defult
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    translates = db.relationship(
        "TranslateModel", back_populates="lang", lazy="dynamic", cascade="all, delete")
