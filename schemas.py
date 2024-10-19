from marshmallow import Schema, fields


class PlainExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    amount = fields.Float(required=True)
    date = fields.Date(required=True)
    category_id = fields.Int(required=True)
    receipt_url = fields.Str(dump_only=True)


class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainCategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()


class PlainLangSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class PlainTranslateSchema(Schema):
    id = fields.Int(dump_only=True)
    key = fields.Str(required=True)
    value = fields.Str(required=True)
    lang_id = fields.Int(required=True)


class ExpenseSchema(PlainExpenseSchema):
    user = fields.Nested(PlainUserSchema(), dump_only=True)
    category = fields.Nested(PlainCategorySchema(), dump_only=True)


# on update an item none of the fields is required
class ExpenseUpdateSchema(Schema):
    name = fields.Str()
    amount = fields.Float()
    date = fields.Date()
    description = fields.Str()
    category_id = fields.Int()
    receipt_url = fields.Str(dump_only=True)


class CategorySchema(PlainCategorySchema):
    user = fields.Nested(PlainUserSchema(), dump_only=True)
    expenses = fields.List(fields.Nested(PlainExpenseSchema()), dump_only=True)


class LangSchema(PlainLangSchema):
    translates = fields.List(fields.Nested(
        PlainTranslateSchema()), dump_only=True)


class TranslateSchema(PlainTranslateSchema):
    lang = fields.Nested(PlainLangSchema(), dump_only=True)


class CategoryUpdateSchema(Schema):
    name = fields.Str()
    description = fields.Str()


class LangUpdateSchema(Schema):
    name = fields.Str()


class TranslateUpdateSchema(Schema):
    value = fields.Str()
    lang_id = fields.Int()


class UserSchema(PlainUserSchema):
    expenses = fields.List(fields.Nested(PlainExpenseSchema()), dump_only=True)
    categories = fields.List(fields.Nested(
        PlainCategorySchema()), dump_only=True)


class GeneralDeclarationSchema(Schema):
    lang_id = fields.Int(required=True)  # Default language
    translations = fields.Dict(
        keys=fields.Str(), values=fields.Str(), required=True)
    langs = fields.Dict(
        keys=fields.Str(), values=fields.Str(), required=True)
