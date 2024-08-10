from marshmallow import Schema, fields


class PlainExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    amount = fields.Float(required=True)
    date = fields.Date(required=True)
    category_id = fields.Int(required=True)


class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainCategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()


class ExpenseSchema(PlainExpenseSchema):
    user = fields.Nested(PlainUserSchema(), dump_only=True)
    category = fields.Nested(PlainCategorySchema(), dump_only=True)


class CategorySchema(PlainCategorySchema):
    user = fields.Nested(PlainUserSchema(), dump_only=True)


class UserSchema(PlainUserSchema):
    expenses = fields.List(fields.Nested(PlainExpenseSchema()), dump_only=True)
    categories = fields.List(fields.Nested(
        PlainCategorySchema()), dump_only=True)
