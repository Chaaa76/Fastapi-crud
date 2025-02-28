from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext

app = FastAPI()

# Temp data storage
users = []
user_id_counter = 1

# Password hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User model for input validation
class UserCreate(BaseModel):
    username: str
    password: str
    contact: Optional[str] = None
    barangay: Optional[str] = None
    role: str = "resident"

# hash pass 
def get_hashed_password(password: str):
    return pwd_context.hash(password)

#if user exists
def get_user_by_username(username: str):
    for user in users:
        if user["username"] == username:
            return user
    return None

@app.post("/users/")
def create_user(user: UserCreate, is_admin: bool = False):
    global user_id_counter

    if user.role == "admin" and not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create other admins.")

    # duplicate username
    if get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already taken.")

    new_user = {
        "id": user_id_counter,
        "username": user.username,
        "password": get_hashed_password(user.password),
        "contact": user.contact,
        "barangay": user.barangay,
        "role": user.role
    }

    users.append(new_user)
    user_id_counter += 1

    return {"message": "User created successfully", "user": new_user}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/")
def get_all_users():
    return users

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate):
    for u in users:
        if u["id"] == user_id:
            u["username"] = user.username
            u["password"] = get_hashed_password(user.password)  # Hash new password
            u["contact"] = user.contact
            u["barangay"] = user.barangay
            u["role"] = user.role
            return {"message": "User updated successfully", "user": u}

    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    global users
    for user in users:
        if user["id"] == user_id:
            users = [u for u in users if u["id"] != user_id]
            return {"message": "User deleted successfully"}

    raise HTTPException(status_code=404, detail="User not found")
