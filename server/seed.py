from datetime import date
from config import app, db
from models import User, Expense, Budget

with app.app_context():
    print("Clearing database...")
    Expense.query.delete()
    User.query.delete()
    Budget.query.delete()
    
    print("Creating users...")
    
    
    
    sample_users = [
        {'username': 'WealthyWarren', 'email': 'warren@stocks.com', 'password': 'warren_secure_99'},
        {'username': 'BudgetBella', 'email': 'bella@save.org', 'password': 'bella_saves_2024'},
        {'username': 'StudentSam', 'email': 'sam@edu.edu', 'password': 'study_hard_sleep_less'},
        {'username': 'ChefCharlie', 'email': 'charlie@kitchen.com', 'password': 'knife_skills_101'},
        {'username': 'DrDan', 'email': 'dan@hospital.net', 'password': 'doctor_dan_77'},
        {'username': 'ArtistAlice', 'email': 'alice@gallery.io', 'password': 'paint_the_world'},
        {'username': 'GymGabe', 'email': 'gabe@fitness.com', 'password': 'heavy_lifts_only'},
        {'username': 'TechTina', 'email': 'tina@code.dev', 'password': 'python_is_life_404'},
        {'username': 'HikerHolly', 'email': 'holly@trails.com', 'password': 'mountains_are_calling'},
        {'username': 'FreelanceFred', 'email': 'fred@work.com', 'password': 'remote_work_king'}
    ]
    
    users_list = []
    for data in sample_users:
        #Create user with standard columns only
        u = User(
            username=data['username'], 
            email=data['email'], 
        )
        #  Set password_hash separately (This triggers the @setter in models.py)
        u.password_hash = data['password']
        
        users_list.append(u)

    db.session.add_all(users_list)
    db.session.commit()
    print("Successfully added users!")
    
    
    #add expenses
    print("Seeding personal expenses...")
    expenses_list = [
        Expense(title='Grocery Run', amount=120.50, category='Food', date=date(2026, 4, 1), description='Weekly restock at Carrefour', user=users_list[0]),
        Expense(title='Netflix Sub', amount=15.00, category='Entertainment', date=date(2026, 4, 2), description='Monthly premium plan', user=users_list[1]),
        Expense(title='Internet Bill', amount=60.00, category='Utilities', date=date(2026, 4, 3), description='Home WiFi for coding', user=users_list[2]),
        Expense(title='Gym Membership', amount=45.00, category='Health', date=date(2026, 4, 4), description='Monthly gym fee', user=users_list[6]),
        Expense(title='Self-Care Day', amount=150.00, category='Maintenance', date=date(2026, 4, 5), description='Hair and nails appointment', user=users_list[7]),
        Expense(title='Starbucks Coffee', amount=6.50, category='Food', date=date(2026, 4, 5), description='Late night study session', user=users_list[2]),
        Expense(title='Electricity', amount=85.00, category='Utilities', date=date(2026, 4, 6), user=users_list[4]),
        Expense(title='Medical Checkup', amount=100.00, category='Health', date=date(2026, 4, 7), description='Annual physical', user=users_list[4]),
        Expense(title='Art Supplies', amount=150.00, category='Hobbies', date=date(2026, 4, 8), description='Oil paints and canvases', user=users_list[5]),
        Expense(title='Render Deployment Fee', amount=7.00, category='Development', date=date(2026, 4, 9), description='Hosting for my first full-stack app!', user=users_list[9])
    ]

    db.session.add_all(expenses_list)
    db.session.commit()

    print("Successfully added your personal expenses! 🚀")
    
    
    print("Seeding monthly budgets...")
    budget_list = [
        Budget(month=4, year=2026, monthly_income=15000.0, monthly_budget=5000.0, user=users_list[0]),
        Budget(month=4, year=2026, monthly_income=3200.0, monthly_budget=1200.0, user=users_list[1]),
        Budget(month=4, year=2026, monthly_income=1200.0, monthly_budget=800.0, user=users_list[2]),
        Budget(month=4, year=2026, monthly_income=4500.0, monthly_budget=2200.0, user=users_list[3]),
        Budget(month=4, year=2026, monthly_income=12000.0, monthly_budget=6000.0, user=users_list[4]),
        Budget(month=4, year=2026, monthly_income=2800.0, monthly_budget=1500.0, user=users_list[5]),
        Budget(month=4, year=2026, monthly_income=3800.0, monthly_budget=1000.0, user=users_list[6]),
        Budget(month=4, year=2026, monthly_income=9500.0, monthly_budget=3500.0, user=users_list[7]),
        Budget(month=4, year=2026, monthly_income=4100.0, monthly_budget=1800.0, user=users_list[8]),
        Budget(month=4, year=2026, monthly_income=5500.0, monthly_budget=2500.0, user=users_list[9])
    ]
    db.session.add_all(budget_list)
    db.session.commit()
    print('Successfully added all budgets')