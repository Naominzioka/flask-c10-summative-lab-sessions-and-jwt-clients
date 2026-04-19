# Personal Expenses Tracker API (Flask + JWT)

Backend-focused Flask API for user authentication, expense tracking, and budgeting using JWT.

The `client-with-jwt` app is included only to demonstrate how tokens are sent from a frontend and how authenticated state appears in the browser.  
`client_with_sessions` is not part of this project scope.

---

## Project Scope

This project provides a backend API with:

- User signup and login
- JWT token-based authentication
- Protected routes
- User-linked expense data
- User-linked budget data
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

This repository uses **Pipenv** with a `Pipfile` and does **not** use `requirements.txt`.

Install backend dependencies with:

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

Create a `.env` file inside `server/`:

```env
JWT_SECRET_KEY=your_secure_jwt_secret
```

---

## Backend Setup and Run

From the project root:

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

You can also start it with Flask CLI:

```bash
cd server
flask --app app run --port 5555
```

---

## Using Flask Shell

To open an interactive Flask shell:

```bash
pipenv shell
cd server
flask shell
```

This is useful for checking models, querying the database, and testing logic manually.

Example:

```python
from models import User, Budget, Expense
from config import db

users = User.query.all()
user = User.query.first()
```

Exit with:

```python
exit()
```

---

## Testing the Backend with Postman

The backend can be tested using **Postman**.

### 1. Sign Up

- **Method:** `POST`
- **URL:** `http://127.0.0.1:5555/signup`

**Body:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "secure_password_123"
}
```

### 2. Log In

- **Method:** `POST`
- **URL:** `http://127.0.0.1:5555/login`

**Body:**
```json
{
  "username": "testuser",
  "password": "secure_password_123"
}
```

A successful login returns a JWT access token.

### 3. Use Bearer Token on Protected Routes

In Postman, add this header:

```http
Authorization: Bearer <access_token>
```

Example protected routes:

- `GET http://127.0.0.1:5555/me`
- `GET http://127.0.0.1:5555/expenses`
- `GET http://127.0.0.1:5555/budgets`

### 4. Test Unauthorized Access

Try a protected route without the `Authorization` header.

Expected result:

- `401 Unauthorized`

---

## JWT Usage

Protected endpoints require a bearer token:

```http
Authorization: Bearer <access_token>
```

The API validates the token on each request and identifies the current user from it.

---

## Budget Summary Calculations (`GET /budgets`)

The budgets endpoint returns additional calculated fields to help users track their spending:

- `total_spent` — total of all expenses linked to that budget
- `remaining_income` — `monthly_income - total_spent`
- `remaining_budget` — `monthly_budget - total_spent`
- `over_budget` — `true` if `total_spent > monthly_budget`

These values are calculated at request time and are not stored in the database.

### Example response item

```json
{
  "id": 1,
  "month": 4,
  "year": 2026,
  "monthly_income": 5000.0,
  "monthly_budget": 3000.0,
  "total_spent": 3450.0,
  "remaining_income": 1550.0,
  "remaining_budget": -450.0,
  "over_budget": true
}
```

---

## Data Model Overview

### User
- unique `username`
- unique `email`
- hashed password

### Budget
- `monthly_income`
- `monthly_budget`
- `month`
- `year`
- belongs to a user

### Expense
- `title`
- `amount`
- `category`
- `date`
- `description`
- belongs to a user
- can be associated with a budget

---

## Migrations

Migration files are located in:

- `server/migrations/versions/b2014e9f7491_initial_migration.py`
- `server/migrations/versions/4872cbd5ebe8_associate_expenses_witha_budget.py`

Apply migrations with:

```bash
cd server
flask db upgrade
```

---

## Frontend Demo Run (Optional)

The frontend is only for demonstrating JWT flow with the backend.

```bash
cd client-with-jwt
npm install
npm start
```

Frontend runs on:

- `http://127.0.0.1:4000`

---

## Notes

- This is primarily a backend project.
- The frontend is included only for JWT demonstration.
- CORS is enabled to allow frontend-backend communication.
- Postman can be used to test all protected routes with a bearer token.
- `flask shell` is useful for manual database inspection and debugging.

---

## License

Educational use.