# from marshmallow import Schema, fields, validate, ValidationError

# class UserSchema(Schema):
#     name = fields.String(required=True, validate=validate.Length(min=3, max=50))
#     username = fields.String(required=True, validate=validate.Length(min=3, max=50))
#     email = fields.Email(required=True)
#     password = fields.String(required=True, validate=validate.Length(min=6))
#     gender = fields.Boolean()
#     role = fields.String(validate=validate.OneOf(["user", "admin"]))

# # For login validation
# class LoginSchema(Schema):
#     username = fields.String(required=True)
#     password = fields.String(required=True)
