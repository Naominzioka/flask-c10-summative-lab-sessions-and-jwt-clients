# Personal Finance Tracker API (Flask + JWT)

Backend-focused Flask project for user authentication, expense tracking, and budgeting using JWT.

The `client-with-jwt` app is included only to demonstrate how tokens are sent from a frontend and how authenticated state appears in the browser.  
`client_with_sessions` is not part of this project scope.

---

## Project Scope

This project delivers a **backend API** with:

- User signup/login
- JWT token-based authentication
- Protected routes
- User-linked budget and expense data
- Database migrations and seeding

---

## Tech Stack

### Backend (`server/`)
- Python 3.8
- Flask 2.2.2
- Flask-RESTful 0.3.9
- Flask-SQLAlchemy 3.0.3
- Flask-Migrate 4.0.0
- Flask-Bcrypt 1.0.1
- Flask-JWT-Extended
- Flask-CORS
- Marshmallow 3.20.1
- SQLAlchemy
- python-dotenv

### Frontend demo (`client-with-jwt/`)
- React

---

## Dependencies

This repository uses **Pipenv** (`Pipfile`) and does **not** use `requirements.txt`.

Install backend dependencies:

```bash
pipenv install
pipenv shell
```

---

## Repository Structure

```text
.
├── Pipfile
├── README.md
├── server
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── schema.py
│   ├── seed.py
│   ├── instance/
│   └── migrations/
└── client-with-jwt
    ├── package.json
    ├── public/
    └── src/
```

---

## Environment Variables

Create a `.env` file (recommended inside `server/`):

```env
JWT_SECRET_KEY=your_secure_jwt_secret
```

---

## Backend Setup & Run

From project root:

```bash
pipenv install
pipenv shell
cd server
flask db upgrade
python seed.py   # optional
python app.py
```

Backend runs on:

- `http://127.0.0.1:5555`

---

## Running with Flask Shell

To run the backend in an interactive Flask shell:

```bash
pipenv shell
cd server
flask shell
```

Inside the shell, you can:

```python
# Access the app context
from app import app
from models import User, Budget, Expense
from config import db

# Query users
users = User.query.all()

# Create objects
new_user = User(username='testuser', email='test@example.com', password='secure123')
db.session.add(new_user)
db.session.commit()

# Check relationships
user = User.query.first()
print(user.expenses)
print(user.budgets)
```

Exit with:

```python
exit()
```

---

## Testing with Postman

### 1. Signup/Login Flow

**Signup:**
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5555/signup`
- **Body** (JSON):
  ```json
  {
    "username": "testuser",
    "email": "test@example.com",
    "password": "secure_password_123"
  }
  ```
- **Response**: JWT token

**Login:**
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5555/login`
- **Body** (JSON):
  ```json
  {
    "username": "testuser",
    "password": "secure_password_123"
  }
  ```
- **Response**: JWT access token

### 2. Using Bearer Token in Protected Routes

Copy the token from signup/login response.

**Example: Get Current User (`/me`)**
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5555/me`
- **Headers**:
  ```
  Authorization: Bearer <your_access_token>
  ```
- **Response**: Current user data

**Example: List User Expenses**
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5555/expenses`
- **Headers**:
  ```
  Authorization: Bearer <your_access_token>
  ```

**Example: Create an Expense**
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5555/expenses`
- **Headers**:
  ```
  Authorization: Bearer <your_access_token>
  Content-Type: application/json
  ```
- **Body** (JSON):
  ```json
  {
    "title": "Groceries",
    "amount": 85.50,
    "category": "Food",
    "date": "2026-04-19",
    "description": "Weekly grocery shopping"
  }
  ```

### 3. Testing Without Token

Try accessing a protected route **without** the `Authorization` header:

- **Method**: `GET`
- **URL**: `http://127.0.0.1:5555/expenses`
- **Expected**: `401 Unauthorized`

---

## JWT Usage

For all protected endpoints, include the bearer token:

```http
Authorization: Bearer <access_token>
```

The API validates JWT on incoming protected requests and resolves the current user from token identity.

---

## Data Model (High-Level)

- `User`
  - unique `username`
  - unique `email`
  - hashed password
- `Budget`
  - monthly income, monthly budget, month, year
  - belongs to a user
- `Expense`
  - date, category, title, amount
  - belongs to a user (and associated budget via later migration)

---

## Migrations

Migration files are in:

- `server/migrations/versions/b2014e9f7491_initial_migration.py`
- `server/migrations/versions/4872cbd5ebe8_associate_expenses_witha_budget.py`

Apply migrations:

```bash
cd server
flask db upgrade
```

---

## Frontend Demo Run (Optional)

```bash
cd client-with-jwt
npm install
npm start
```

Frontend demo runs on:

- `http://127.0.0.1:4000`

---

## Notes

- Backend is the main deliverable.
- Frontend exists only to demonstrate JWT client behavior.
- CORS is enabled in backend config for client integration.
- Use Postman to test API endpoints with bearer tokens.
- Use `flask shell` for database queries and testing in the Python REPL.

---

## License

Educational use.