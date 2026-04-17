from marshmallow import Schema, fields, validates_schema, ValidationError

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username= fields.Str(required=True)
    email = fields.Email()
    monthly_income = fields.Float()
    monthly_budget = fields.Float()
    
    @validates_schema
    def validate(self, data, **kwargs):
        if data.get('monthly_budget') is not None and data['monthly_budget'] < 0:
            raise ValidationError('Monthly budget cannot be a negative number.')
        if data.get('monthly_income') is not None and data['monthly_income'] < 0:
            raise ValidationError('Monthly income cannot be a negative integer.')
        
class ExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date()
    category = fields.Str(required=True)
    title = fields.Str(required=True)
    amount = fields.Float(required=True)
    description = fields.Str(allow_none=True)
    
    @validates_schema
    def validate(self, data, **kwargs):
        if data.get('amount') is not None and data['amount'] < 0:
            raise ValidationError('Amount cannot be negative.')
        if data.get('title') is not None and len(data['title']) > 80:
            raise ValidationError('Title should not exceed 80 characters.')
        if data.get('category') is not None and len(data['category']) > 30:
            raise ValidationError('Category should not exceed 30 characters.')
        if data.get('description') is not None and len(data['description']) > 200:
            raise ValidationError('Description should not exceed 200 characters.')
        