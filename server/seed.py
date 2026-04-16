from datetime import date
from config import app, db
from models import User, Expense

with app.app_context():
    print("Clearing database...")
    Expense.query.delete()
    User.query.delete()
    
    print("Creating users...")
    
    users_list = []
    
