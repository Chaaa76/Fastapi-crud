# FastAPI User Management API

## Features
- **Create a user** with username, password, contact, and barangay.
- **Retrieve a user** by ID.
- **Retrieve all users**.
- **Update user details**.
- **Delete a user**.

## Installation
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <your-project-folder>
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   ```
## Running the API
Run the FastAPI application with Uvicorn:
```bash
uvicorn main:app --reload
```

- The API will be available at: `http://127.0.0.1:8000`
- The interactive API docs can be accessed at:
  - Swagger UI: `http://127.0.0.1:8000/docs`
  - ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### 1. Create a User
- **Endpoint:** `POST /users/`
- **Request Body:**
  ```json
  {
    "username": "john_doe",
    "password": "securepass",
    "contact": "09123456789",
    "barangay": "Sample Barangay"
  }
  ```
- **Response:**
  ```json
  {
    "message": "User created successfully",
    "user": { "id": 1, "username": "john_doe", "password": "securepass", "contact": "09123456789", "barangay": "Sample Barangay" }
  }
  ```

### 2. Get a User by ID
- **Endpoint:** `GET /users/{user_id}`
- **Response:**
  ```json
  { "id": 1, "username": "john_doe", "password": "securepass", "contact": "09123456789", "barangay": "Sample Barangay" }
  ```

### 3. Get All Users
- **Endpoint:** `GET /users/`
- **Response:**
  ```json
  [
    { "id": 1, "username": "john_doe", "password": "securepass", "contact": "09123456789", "barangay": "Sample Barangay" }
  ]
  ```

### 4. Update a User
- **Endpoint:** `PUT /users/{user_id}`
- **Request Body:**
  ```json
  {
    "username": "new_username",
    "password": "new_password",
    "contact": "09987654321",
    "barangay": "New Barangay"
  }
  ```
- **Response:**
  ```json
  { "message": "User updated successfully", "user": { "id": 1, "username": "new_username", "password": "new_password", "contact": "09987654321", "barangay": "New Barangay" } }
  ```

### 5. Delete a User
- **Endpoint:** `DELETE /users/{user_id}`
- **Response:**
  ```json
  { "message": "User deleted successfully" }
  ```

## Notes
- This API uses an in-memory list (`users` list) as a temporary database.
- Passwords are stored in plain text (not secure)
- No persistent database integration (SQLite, PostgreSQL, MongoDB, etc.) yet.

## Future Improvements
- Implement a database (PostgreSQL, SQLite, or MongoDB).
- Use password hashing for security.
- Add authentication & authorization (OAuth, JWT, etc.).
- Implement proper error handling and validation.


### Author
Developed by **Techxplorers** 🚀
