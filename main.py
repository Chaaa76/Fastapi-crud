from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# Temp data storage
users = []
user_id_counter = 1  # Incremental ID 

# Pydantic model 
class UserCreate(BaseModel):
    username: str
    password: str
    contact: Optional[str] = None
    barangay: Optional[str] = None
    role: str = "resident"  # Default role is 'resident'

@app.post("/users/")
def create_user(user: UserCreate):
    global user_id_counter

    if user.role not in ["resident", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'resident' or 'admin'.")

    new_user = {
        "id": user_id_counter,
        "username": user.username,
        "password": user.password,  # Not secure 
        "contact": user.contact,
        "barangay": user.barangay,
        "role": user.role
    }

    users.append(new_user)
    user_id_counter += 1  # Increment user ID

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
            u["password"] = user.password
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
