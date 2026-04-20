
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from flask import request, jsonify, make_response
from datetime import datetime
from collections import OrderedDict

from models import User, Expense, Budget
from schema import UserSchema, ExpenseSchema, BudgetSchema
from config import app, db, api, jwt

"""
User state is maintained through stateless JWT authentication, 
where the server issues a signed token upon login that the client stores in its own browser storage.
Because the server does not "remember" sessions, the frontend maintains
the logged-in state by attaching this token to the Authorization header of every subsequent request.
The server global guard(@app.before_request) then verifies the 
tokens signature in real-time and uses get_jwt_identity() 
to securely extract the users ID and filter their private data.
"""
#setup endpoints
@app.before_request  #protected routes
def check_if_logged_in():
    open_access_list = ['signup', 'login']
    
    if request.endpoint in open_access_list:
        return None
    try:
        verify_jwt_in_request()
    except Exception:
        return make_response(jsonify({'errors': ['401 Unauthorized']}), 401) #stops any request without a valid token

#new user endpoint    
class Signup(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'errors': ['Signup failed. Please try again.']}), 400)
        try:
            request_json = request.get_json()
        except Exception:
            return make_response(jsonify({'errors': ['Signup failed. Please try again.']}), 400)
        
        username = request_json.get('username')
        password = request_json.get('password')
        email = request_json.get('email')

        if not username:
            return make_response(jsonify({'errors': ['Username is required']}), 400)
        if not email:
            return make_response(jsonify({'errors': ['Email is required']}), 400)
        if not password:
            return make_response(jsonify({'errors': ['Password is required']}), 400)

        try:
            new_user = User(
                username=username,
                email=email
            )
            new_user.password_hash=password
            db.session.add(new_user)
            db.session.commit()
            access_token = create_access_token(identity=str(new_user.id))  #converts user id to string for JWT identity payload
            return make_response(jsonify(token=access_token, user=UserSchema().dump(new_user)), 201)
        except ValueError as exc:
            db.session.rollback()
            return make_response(jsonify({'errors': [str(exc)]}), 422)
        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({'errors': ['Username or email already exists']}), 422) #prevents duplicate usernames or emails from crashing the server

#login route
class Login(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)
        try:
            request_json = request.get_json()
        except Exception:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)

        username = request_json.get('username')
        password = request_json.get('password')

        if not username or not password:
            return make_response(jsonify({'errors': ['Username and password are required']}), 400)
        
        user = User.query.filter(User.username == username).first()
        if user and user.authenticate(password):
            token = create_access_token(identity=str(user.id))
            return make_response(jsonify(token=token, user=UserSchema().dump(user)), 200)
        
        return make_response(jsonify({'errors': ['Invalid username or password']}), 401)
    

class WhoAmI(Resource):
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user:
            return make_response(jsonify({'errors': ['User not found']}), 404)
        
        return make_response(jsonify(UserSchema().dump(user)), 200)
    
    """ 
    NOTE:This API uses stateless JWTs. Logout is handled on the 
    frontend by deleting the stored token. Since the backend doesn't track 
    sessions, destroying the token on the client side instantly kills access, 
    making a dedicated server-side logout route unnecessary.
    """
    
class ExpensesIndex(Resource): 
    def get(self):
        user_id = get_jwt_identity()
        page= request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)
        pagination = Expense.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)  #use paginate to limit the number of records returned 
        if not pagination.items:                                                                                        #this improves server perfomance and prevents UI overload
            return make_response(jsonify({'errors': ['No expenses found']}), 404)
        return {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "items": ExpenseSchema(many=True).dump(pagination.items)}, 200
        
   # POST request to add a new expense
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)
        try:
            data = request.get_json()
        except Exception:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)

        user_id = get_jwt_identity()
        date_str = data.get('date')

        if not date_str:
            return make_response(jsonify({'errors': ['Add a date before saving this expense.']}), 400)
        
        # Convert string date to a real date object
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return make_response(jsonify({'errors': ['Date format should be YYYY-MM-DD (example: 2026-04-21).']}), 400)

        #Find or Create the Budget
        budget = Budget.query.filter_by(user_id=user_id, month=dt.month, year=dt.year).first()
        
        if not budget:
            budget = Budget(month=dt.month, year=dt.year, user_id=user_id, monthly_income=0, monthly_budget=0)
            db.session.add(budget)
            db.session.commit()

        #Create the Expense
        new_expense = Expense(
            title=data.get('title'),
            amount=data.get('amount'),
            category=data.get('category'),
            description=data.get('description'),
            date=dt.date(),
            user_id=user_id,
            budget_id=budget.id #ties the expense to the budget 
            
        )
        try:
            db.session.add(new_expense)
            db.session.commit()
            return make_response(jsonify(ExpenseSchema().dump(new_expense)), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'errors': [str(e)]}), 422)
            
# find one expense by its id
class ExpensesById(Resource):
    def get(self, id):
        user_id = get_jwt_identity()
        user_expenses = Expense.query.filter_by(id=id, user_id=user_id).first()  # filter by both id and user id so users can't access other users data
        if not user_expenses:
            return make_response(jsonify({'errors': ['Expense not found']}), 404)
        return make_response(jsonify(ExpenseSchema().dump(user_expenses)), 200)
    
    #delete an expense by id
    def delete(self, id):
        user_id = get_jwt_identity()
        user_expense = Expense.query.filter_by(id=id, user_id=user_id).first()
        if not user_expense:
            return make_response(jsonify({'errors': ['Expense id not found']}), 404)
        try:
            db.session.delete(user_expense)
            db.session.commit()
            return make_response('', 204)  # return empty since no content is found after the deletion
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'errors': ['Could not delete expense']}), 500)
    
    def patch(self, id):
        if not request.is_json:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)
        try:
            data = request.get_json()
        except Exception:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)

        user_id = get_jwt_identity()
        user_expense = Expense.query.filter_by(id=id, user_id=user_id).first()
        if not user_expense:
            return make_response(jsonify({'errors': ['Expense not found']}), 404)

        if not data:
            return make_response(jsonify({'errors': ['No update data provided']}), 400)
        
        # Update only the fields available in the request body
        for key in ['title', 'amount', 'category', 'description']:
            if key in data:
                setattr(user_expense, key, data[key])
        try:
            db.session.commit()
            return make_response(jsonify(ExpenseSchema().dump(user_expense)), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'errors': [str(e)]}), 422)
                
#budget endpoints
# 1.all user budgets with calculated fields for total spent, remaining budget, and remaining income
class BudgetIndex(Resource):
    def get(self):
        user_id = get_jwt_identity()
        user_budgets = Budget.query.filter_by(user_id=user_id).all()
        
        if not user_budgets:
            return make_response(jsonify({'errors': ['No budgets found.']}), 404)

        results = []
        
        for b in user_budgets:
            budget_data = BudgetSchema().dump(b)
            
            total_spent = 0                    
            for expense in b.expenses:
                total_spent += expense.amount  # calculate total spent for each budget by summing the amounts of all linked expenses
                                               #the user is given real time budget summary without manual calculations.
            ordered = OrderedDict()
            ordered['id'] = budget_data.get('id')
            ordered['month'] = budget_data.get('month')
            ordered['year'] = budget_data.get('year')
            ordered['monthly_income'] = budget_data.get('monthly_income')
            ordered['monthly_budget'] = budget_data.get('monthly_budget')
            ordered['total_spent'] = round(float(total_spent), 2)
            ordered['remaining_income'] = round(float(b.monthly_income - total_spent), 2)
            ordered['remaining_budget'] = round(float(b.monthly_budget - total_spent), 2)
            ordered['over_budget'] = total_spent > b.monthly_budget
            
            results.append(ordered)

        return make_response(jsonify(results), 200)

    #create new budget
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)
        try:
            data = request.get_json()
        except Exception:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)

        user_id = get_jwt_identity()

        if data.get('month') is None or data.get('year') is None:
            return make_response(jsonify({'errors': ['Month and year are required']}), 400)
    
        check_if_exists = Budget.query.filter_by(
            user_id=user_id,
            month = data.get('month'),
            year = data.get('year')
        ).first()
        if check_if_exists:
            return make_response(jsonify({'errors': ['Budget for this month already exists']}), 422)
        new_budget = Budget(
            monthly_income = data.get('monthly_income'),
            monthly_budget = data.get('monthly_budget'),
            month= data.get('month'),
            year=data.get('year'),
            user_id=user_id
        )
        try:
            db.session.add(new_budget)
            db.session.commit()
            return make_response(jsonify(BudgetSchema().dump(new_budget)), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'errors': [str(e)]}), 422)
        
        
        
        
class BudgetId(Resource):
    def get(self, id):
        user_id = get_jwt_identity()
        user_budget = Budget.query.filter_by(id=id, user_id=user_id).first()
        if not user_budget:
            return make_response(jsonify({'errors': ['Budget not found']}), 404)
        return make_response(jsonify(BudgetSchema().dump(user_budget)), 200)
    
    def delete(self, id):
        user_id = get_jwt_identity()
        user_budget = Budget.query.filter_by(id=id, user_id=user_id).first()
        if not user_budget:
            return make_response(jsonify({'errors': ['Budget not found']}), 404)
        try:
            Expense.query.filter_by(budget_id=id).delete()  #first find expenses linked to the budget to be deleted and delete them
            db.session.delete(user_budget)
            db.session.commit()
            return make_response('', 204)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'errors': [str(e)]}), 500)
    
    def patch(self, id):
        if not request.is_json:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)
        try:
            data = request.get_json()
        except Exception:
            return make_response(jsonify({'errors': ['Something went wrong. Please try again.']}), 400)

        user_id = get_jwt_identity()
        user_budget = Budget.query.filter_by(id=id, user_id=user_id).first()
        if not user_budget:
            return make_response(jsonify({'errors': ['Budget not found']}), 404)

        if not data:
            return make_response(jsonify({'errors': ['No update data provided']}), 400)
        
        # Update only the fields available in the request body
        for key in ['monthly_income', 'monthly_budget']:
            if key in data:
                setattr(user_budget, key, data[key])
        try:
            db.session.commit()
            return make_response(jsonify(BudgetSchema().dump(user_budget)), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'errors': [str(e)]}), 422)
        

    

api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(WhoAmI, '/me', endpoint='me')
api.add_resource(ExpensesById, '/expenses/<int:id>', endpoint='expensesId' )
api.add_resource(ExpensesIndex, '/expenses', endpoint='expenses')
api.add_resource(BudgetIndex, '/budgets', endpoint='budgets')
api.add_resource(BudgetId, '/budgets/<int:id>', endpoint='budgetId')


if __name__ == '__main__':
    app.run(port=5555, debug=True)