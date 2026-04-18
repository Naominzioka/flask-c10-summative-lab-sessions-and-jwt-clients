import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_restful import Api
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()

app = Flask(__name__)
# This tells the browser: "It is okay to send the Authorization header to this API"
CORS(app, resources={r"/*": {"origins": "*"}}, expose_headers=["Authorization"], supports_credentials=True)

# --- Configurations ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'       # connection - tells Flask where my db lives
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False             # reduce memory and processing power by not tracking every single change on the db
app.json.compact = False                                         # readability - makes json response easy to read
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY', '')           # security - key to sign tokens

# --- Initializing Tools ---
jwt = JWTManager(app)                                            # handling json web tokens

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})                                                               # best practice incase of changes in my db during an update names remain clear and predictable

db = SQLAlchemy(metadata=metadata)                               # ORM - allows me to interact with my db using Python instead of raw SQL

migrate = Migrate(app, db)                                       # track changes to my db
db.init_app(app)

bcrypt = Bcrypt(app)                                             # for hashing passwords

api = Api(app)                                                   # turns my flask app into a restful API