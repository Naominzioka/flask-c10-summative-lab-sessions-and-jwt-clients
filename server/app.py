from models import User, Expense
from config import app, db, api



if __name__ == '__main__':
    app.run(port=5555, debug=True)