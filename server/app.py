
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

    

api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(WhoAmI, '/me', endpoint='me')

if __name__ == '__main__':
    app.run(port=5555, debug=True)