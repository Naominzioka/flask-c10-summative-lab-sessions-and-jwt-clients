
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from flask import request, jsonify, make_response

from models import User, Expense
from schema import UserSchema, ExpenseSchema
from config import app, db, api, jwt

#setup endpoints
@app.before_request
def check_if_logged_in():
    open_access_list = ['signup', 'login']
    
    if request.endpoint not in open_access_list and not verify_jwt_in_request():
        return {'errors': ['401 Unauthorized']}, 401
    
class Signup(Resource):
    def post(self):
        request_json = request.get_json()
        
        username = request_json.get('username')
        password = request_json.get('password')
        email = request_json.get('email')

#login route
class Login(Resource):
    def post(self):
        usename = request.get_json()['username']
        password = request.get_json()['password']
        
        user = User.query.filter(User.username == usename).first()
        if user and user.authenticate(password):
            token = create_access_token(identity=str(user.id))
            return make_response(jsonify(token=token, user=UserSchema().dump(user)), 200)
        
        return {'errors': ['401 Unauthorized']}, 401
    

api.add_resource(Login, '/login', endpoint='login')

if __name__ == '__main__':
    app.run(port=5555, debug=True)