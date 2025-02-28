from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# temp dataholder
users = []
user_id_counter = 1  # inc for id for every new use

# pydantic for data validation
class UserCreate(BaseModel):
    username: str
    password: str
    contact: Optional[str] = None
    barangay: Optional[str] = None

@app.post("/users/")
def create_user(user: UserCreate):
    global user_id_counter

    # temp dictionary
    new_user = {
        "id": user_id_counter,
        "username": user.username,
        "password": user.password,  #  not secure
        "contact": user.contact,
        "barangay": user.barangay
    }

    users.append(new_user)
    user_id_counter += 1  # inc for id for every new user

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
