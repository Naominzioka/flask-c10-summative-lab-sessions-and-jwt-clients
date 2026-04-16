from config import db, bcrypt
from sqlalchemy.orm import validates
import re
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String,unique=True, nullable=False)
    email = db.Column(db.String, unique=True)
    _password_hash = db.Column(db.String)
    monthly_income = db.Column(db.Float, default=0.0)
    monthly_budget=db.Column(db.Float, default=0.0)
    
    #one to many relationship where one user has many expenses..so we keep expenses on the one side & user_id on the many side
    expenses = db.relationship('Expense', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username},ID {self.id}>'
    
    @hybrid_property
    def _password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')
    
    @_password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')
        
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
            
    #add user validation
    @validates('email', 'monthly_budget', 'monthly_income')
    def validate_user(self, key, value):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if key == 'email':
            if value and not re.match(email_pattern, value):
                raise ValueError('Invalid email address format (e.g., user@example.com)')
        if key == 'monthly_budget':
            if value < 0:
                raise ValueError(f'{key} cannot be a negative number')
        if key == 'monthly_income':
            if value < 0:
                raise ValueError(f'{key} cannot be a negative number')
            
        return value
    
class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable =False)
    category = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<{self.title}, {self.amount}>'
    
    #foreign key linking to every user in Users table
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='expenses')
    
    @validates('amount', 'description', 'title', 'category')
    def validate_expense(self, key, value):
        if key == 'amount':
            if value < 0:
                raise ValueError('Amount must be a positive number')
        if key == 'description':
            if len(value) > 200:
                raise ValueError('Description should not exceed 200 characters long')
        if key == 'title':
            if not value or value.strip() == '':
                raise ValueError('Title cannot be empty to enable easy tracking of expenses')
        if key == 'category':
            if not value or value.strip() == '':
                raise ValueError('Category cannot be empty')
            
        return value
    