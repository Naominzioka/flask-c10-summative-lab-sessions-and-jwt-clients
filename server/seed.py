from datetime import date
from config import app, db
from models import User, Expense, Budget

with app.app_context():
    print("Clearing database...")
    Expense.query.delete()
    Budget.query.delete()
    User.query.delete()
    
    #creating users
    print("Creating users...")
    sample_users = [
        {'username': 'WealthyWarren', 'email': 'warren@stocks.com', 'password': 'warren_secure_99'},
        {'username': 'BudgetBella', 'email': 'bella@save.org', 'password': 'bella_saves_2024'},
        {'username': 'StudentSam', 'email': 'sam@edu.edu', 'password': 'study_hard_sleep_less'},
    ]
    
    users_list = []
    for data in sample_users:
        u = User(username=data['username'], email=data['email'])
        u.password_hash = data['password']
        users_list.append(u)

    db.session.add_all(users_list)
    db.session.commit()
    print("Successfully added users!")
    
    #add budgets
    print("Seeding monthly budgets...")
    # All budgets belong to users_list[0] (WealthyWarren)
    budget_list = [
        Budget(month=4, year=2026, monthly_income=15000.0, monthly_budget=5000.0, user=users_list[0]),
        Budget(month=5, year=2026, monthly_income=15000.0, monthly_budget=5000.0, user=users_list[0]),
    ]
    db.session.add_all(budget_list)
    db.session.commit()
    print('Successfully added all budgets for the first user')
    
    
    
    #add expenses- these expenses belong to one user to enable pagination
    print("Seeding expenses...")
    sample_expenses = [
        {'title': 'Grocery Run', 'amount': 120.50, 'category': 'Food', 'desc': 'Weekly restock at Carrefour'},
        {'title': 'Netflix Sub', 'amount': 15.00, 'category': 'Entertainment', 'desc': 'Monthly premium plan'},
        {'title': 'Internet Bill', 'amount': 60.00, 'category': 'Utilities', 'desc': 'Home WiFi for coding'},
        {'title': 'Gym Membership', 'amount': 45.00, 'category': 'Health', 'desc': 'Monthly gym fee'},
        {'title': 'Self-Care Day', 'amount': 150.00, 'category': 'Maintenance', 'desc': 'Hair and nails appointment'},
        {'title': 'Starbucks Coffee', 'amount': 6.50, 'category': 'Food', 'desc': 'Late night study session'},
        {'title': 'Electricity', 'amount': 85.00, 'category': 'Utilities', 'desc': 'Monthly power bill'},
        {'title': 'Medical Checkup', 'amount': 100.00, 'category': 'Health', 'desc': 'Annual physical'},
        {'title': 'Art Supplies', 'amount': 150.00, 'category': 'Hobbies', 'desc': 'Oil paints and canvases'},
        {'title': 'Render Fee', 'amount': 7.00, 'category': 'Development', 'desc': 'Hosting for full-stack app'}
    ]

    expenses_list = []

    #Loop for April (First 10)
    day_counter = 1
    for item in sample_expenses:
        expenses_list.append(Expense(
            title=item['title'],
            amount=item['amount'],
            category=item['category'],
            description=item['desc'],
            date=date(2026, 4, day_counter),
            user=users_list[0],
            budget=budget_list[0]
        ))
        day_counter += 1

    #Loop for May (Next 10)
    day_counter = 1
    for item in sample_expenses:
        expenses_list.append(Expense(
            title=f"May {item['title']}", # Added 'May' just to distinguish them
            amount=item['amount'],
            category=item['category'],
            description=item['desc'],
            date=date(2026, 5, day_counter),
            user=users_list[0],
            budget=budget_list[1]
        ))
        day_counter += 1

    db.session.add_all(expenses_list)
    db.session.commit()
    print("Successfully added expenses! 🚀")