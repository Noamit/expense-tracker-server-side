from db import db


class TranslateModel(db.Model):
    __tablename__ = "translates"

    # auto-increment by defult
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    lang_id = db.Column(
        db.Integer, db.ForeignKey("langs.id"), unique=False, nullable=False
    )

    lang = db.relationship("LangModel", back_populates="translates")
