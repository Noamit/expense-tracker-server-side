from marshmallow import Schema, fields


class PlainExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    amount = fields.Float(required=True)
    date = fields.Date(required=True)


class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class ExpenseSchema(PlainExpenseSchema):
    user = fields.Nested(PlainUserSchema(), dump_only=True)


class UserSchema(PlainUserSchema):
    items = fields.List(fields.Nested(PlainExpenseSchema()), dump_only=True)
