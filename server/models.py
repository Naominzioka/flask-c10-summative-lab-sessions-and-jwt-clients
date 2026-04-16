from config import db

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String,unique=True, nullable=False)
    email = db.Column(db.String, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    monthly_income = db.Column(db.Float, default=0.0)
    monthly_budget=db.Column(db.Float, default=0.0)
    
    #one to many relationship where one user has many expenses..so we keep expenses on the one side & user_id on the many side
    expenses = db.relationship('Expense', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username},ID {self.id}>'
    
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