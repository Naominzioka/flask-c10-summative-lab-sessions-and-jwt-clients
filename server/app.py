
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from flask import request, jsonify, make_response
from datetime import datetime

from models import User, Expense, Budget
from schema import UserSchema, ExpenseSchema
from config import app, db, api, jwt

#setup endpoints
@app.before_request
def check_if_logged_in():
    open_access_list = ['signup', 'login']
    
    if request.endpoint in open_access_list:
        return None
    try:
        verify_jwt_in_request()
    except Exception:
        return make_response(jsonify({'errors': ['401 Unauthorized']}), 401)
    
    
#new user endpoint    
class Signup(Resource):
    def post(self):
        request_json = request.get_json()
        
        username = request_json.get('username')
        password = request_json.get('password')
        email = request_json.get('email')
        
        new_user = User(
            username=username,
            email=email
        )
        new_user.password_hash=password
        try:
            db.session.add(new_user)
            db.session.commit()
            access_token = create_access_token(identity=str(new_user.id))
            return make_response(jsonify(token=access_token, user=UserSchema().dump(new_user)), 201)
        except IntegrityError:
            return make_response(jsonify({'errors': ['422 Unprocessable Entity']}), 422)

#login route
class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        password = request.get_json()['password']
        
        user = User.query.filter(User.username == username).first()
        if user and user.authenticate(password):
            token = create_access_token(identity=str(user.id))
            return make_response(jsonify(token=token, user=UserSchema().dump(user)), 200)
        
        return make_response(jsonify({'errors': ['401 Unauthorized']}), 401)
    

class WhoAmI(Resource):
    def get(self):
        user_id = get_jwt_identity()

        user = User.query.filter(User.id == int(user_id)).first()
        if not user:
            return make_response(jsonify({'errors': ['User not found']}), 404)
        
        return UserSchema().dump(user), 200
    
class ExpensesIndex(Resource): 
    def get(self):
        user_id = get_jwt_identity()
        page= request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)
        pagination = Expense.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)  #use paginate to limit the number of records returned 
        if not pagination.items:                                                                                        #this improves server perfomance and prevents UI overload
            return make_response(jsonify({'message': 'No expenses found'}), 404)
        return {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "items": ExpenseSchema(many=True).dump(pagination.items)}, 200
        
   # POST request to add a new expense
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Convert string date to a real date object
        dt = datetime.strptime(data.get('date'), '%Y-%m-%d')

        #Find or Create the Budget
        budget = Budget.query.filter_by(user_id=user_id, month=dt.month, year=dt.year).first()
        
        if not budget:
            month_name = dt.strftime('%B')  #extract the full name of the month
            budget = Budget(name=f"{month_name} Budget", month=dt.month, year=dt.year, user_id=user_id, amount=0)
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
            budget_id=budget.id
            
        )
        try:
            db.session.add(new_expense)
            db.session.commit()
            return ExpenseSchema().dump(new_expense), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 422
        
# find one expense by its id
class ExpensesById(Resource):
    def get(self, id):
        user_id = get_jwt_identity()
        user_expenses = Expense.query.filter_by(id=id, user_id=user_id).first()
        if not user_expenses:
            return make_response(jsonify({'message': 'Expense not found or unauthorized'}), 404)
        return ExpenseSchema().dump(user_expenses), 200

    

api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(WhoAmI, '/me', endpoint='me')
api.add_resource(ExpensesById, '/expenses/<int:id>', endpoint='expensesId' )
api.add_resource(ExpensesIndex, '/expenses', endpoint='expenses')


if __name__ == '__main__':
    app.run(port=5555, debug=True)