from db import db


class TranslateModel(db.Model):
    __tablename__ = "translates"

    # auto-increment by defult
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Text, nullable=False)

    lang_id = db.Column(
        db.Integer, db.ForeignKey("langs.id"), unique=False, nullable=False
    )

    lang = db.relationship("LangModel", back_populates="translates")

    __table_args__ = (
        db.UniqueConstraint('lang_id', 'key', name='uq_lang_id_key'),
    )
