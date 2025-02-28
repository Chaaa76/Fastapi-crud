from fastapi import FastAPI, HTTPException, Depends, Path, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from datetime import datetime
from enum import Enum
from passlib.context import CryptContext

# Initialize FastAPI
app = FastAPI(title="Barangay Management System")

# Password hash utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str):
    return pwd_context.hash(password)


# ResidentStatus Enum according to the UML
class ResidentStatus(str, Enum):
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    APPROVED = "approved"


# =========== MODEL DEFINITIONS ===========
# Base User Model
class UserBase(BaseModel):
    username: str
    password: str
    contact_number: Optional[str] = None
    barangay: Optional[str] = None


class UserCreate(UserBase):
    role: str = "resident"


class UserResponse(BaseModel):
    id: int
    username: str
    contact_number: Optional[str] = None
    barangay: Optional[str] = None
    role: str


# Prompt History Model
class PromptHistoryBase(BaseModel):
    title: str
    prompt: str


class PromptHistoryCreate(PromptHistoryBase):
    pass


class PromptHistoryResponse(PromptHistoryBase):
    id: int
    user_id: int
    created_at: datetime


# Resident-specific models
class ResidentCreate(UserCreate):
    status: ResidentStatus = ResidentStatus.APPROVED


class ResidentUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    contact_number: Optional[str] = None
    barangay: Optional[str] = None
    status: Optional[ResidentStatus] = None


class ResidentResponse(UserResponse):
    status: ResidentStatus
    prompts: List[PromptHistoryResponse] = []


# Admin-specific models
class AdminCreate(UserCreate):
    role: str = "admin"


class AdminResponse(UserResponse):
    pass



users = []
user_id_counter = 1
prompt_histories = []
prompt_id_counter = 1



def get_user_by_username(username: str):
    for user in users:
        if user["username"] == username:
            return user
    return None


def get_user_by_id(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def get_prompts_by_user_id(user_id: int):
    return [p for p in prompt_histories if p["user_id"] == user_id]



@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, is_admin: bool = False):
    global user_id_counter

    # Check admin privileges for creating admin users
    if user.role == "admin" and not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create other admins.")

    # Check for duplicate username
    if get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already taken.")

    # Create new user
    new_user = {
        "id": user_id_counter,
        "username": user.username,
        "password": get_hashed_password(user.password),  # Never return raw password
        "contact_number": user.contact_number,
        "barangay": user.barangay,
        "role": user.role
    }

    # Add resident-specific fields
    if user.role == "resident":
        new_user["status"] = ResidentStatus.APPROVED
        new_user["prompts"] = []

    users.append(new_user)
    user_id_counter += 1

    # Create a copy without password for response
    response_user = new_user.copy()
    del response_user["password"]

    return response_user


@app.get("/users/{user_id}", response_model=Union[ResidentResponse, AdminResponse])
def get_user(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a copy without password for response
    response_user = user.copy()
    del response_user["password"]

    # For residents, include their prompts
    if user["role"] == "resident":
        response_user["prompts"] = get_prompts_by_user_id(user_id)

    return response_user


@app.get("/users/", response_model=List[UserResponse])
def get_all_users():
    response_users = []
    for user in users:
        # Create a copy without password for response
        response_user = user.copy()
        del response_user["password"]
        response_users.append(response_user)

    return response_users


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: Union[ResidentUpdate, UserCreate]):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if hasattr(user_update, "username") and user_update.username:
        # Check if new username already exists
        existing_user = get_user_by_username(user_update.username)
        if existing_user and existing_user["id"] != user_id:
            raise HTTPException(status_code=400, detail="Username already taken")
        user["username"] = user_update.username

    if hasattr(user_update, "password") and user_update.password:
        user["password"] = get_hashed_password(user_update.password)

    if hasattr(user_update, "contact_number"):
        user["contact_number"] = user_update.contact_number

    if hasattr(user_update, "barangay"):
        user["barangay"] = user_update.barangay

    # Handle resident-specific updates
    if user["role"] == "resident" and hasattr(user_update, "status") and user_update.status:
        user["status"] = user_update.status

    # Create a copy without password for response
    response_user = user.copy()
    del response_user["password"]

    return response_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    global users, prompt_histories
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Remove user's prompts if they are a resident
    if user["role"] == "resident":
        prompt_histories = [p for p in prompt_histories if p["user_id"] != user_id]

    # Remove user
    users = [u for u in users if u["id"] != user_id]

    return {"message": "User deleted successfully"}


# =========== RESIDENT STATUS ENDPOINTS ===========
@app.put("/residents/{user_id}/status", response_model=ResidentResponse)
def update_resident_status(
        user_id: int,
        status_update: ResidentStatus,
        is_admin: bool = True  # In a real app, this would be determined through auth
):
    # Only admins should be able to update status
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can update resident status")

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] != "resident":
        raise HTTPException(status_code=400, detail="User is not a resident")

    # Update status
    user["status"] = status_update

    # Create a copy without password for response
    response_user = user.copy()
    del response_user["password"]
    response_user["prompts"] = get_prompts_by_user_id(user_id)

    return response_user


@app.get("/residents/status/{status}", response_model=List[ResidentResponse])
def get_residents_by_status(status: ResidentStatus):
    filtered_users = []

    for user in users:
        if user["role"] == "resident" and user.get("status") == status:
            # Create a copy without password for response
            response_user = user.copy()
            del response_user["password"]
            response_user["prompts"] = get_prompts_by_user_id(user["id"])
            filtered_users.append(response_user)

    return filtered_users


# =========== PROMPT HISTORY ENDPOINTS ===========
@app.post("/residents/{user_id}/prompts/", response_model=PromptHistoryResponse)
def create_prompt(user_id: int, prompt: PromptHistoryCreate):
    global prompt_id_counter

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] != "resident":
        raise HTTPException(status_code=400, detail="User is not a resident")

    # Create new prompt
    new_prompt = {
        "id": prompt_id_counter,
        "title": prompt.title,
        "prompt": prompt.prompt,
        "user_id": user_id,
        "created_at": datetime.now()
    }

    prompt_histories.append(new_prompt)
    prompt_id_counter += 1

    return new_prompt


@app.get("/residents/{user_id}/prompts/", response_model=List[PromptHistoryResponse])
def get_user_prompts(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] != "resident":
        raise HTTPException(status_code=400, detail="User is not a resident")

    # Get all prompts for this user
    return get_prompts_by_user_id(user_id)


@app.get("/prompts/{prompt_id}", response_model=PromptHistoryResponse)
def get_prompt(prompt_id: int):
    for prompt in prompt_histories:
        if prompt["id"] == prompt_id:
            return prompt

    raise HTTPException(status_code=404, detail="Prompt not found")


@app.put("/prompts/{prompt_id}", response_model=PromptHistoryResponse)
def update_prompt(prompt_id: int, prompt_update: PromptHistoryCreate):
    for prompt in prompt_histories:
        if prompt["id"] == prompt_id:
            prompt["title"] = prompt_update.title
            prompt["prompt"] = prompt_update.prompt
            # We don't update created_at to preserve the original creation time
            return prompt

    raise HTTPException(status_code=404, detail="Prompt not found")


@app.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: int):
    global prompt_histories

    for prompt in prompt_histories:
        if prompt["id"] == prompt_id:
            prompt_histories = [p for p in prompt_histories if p["id"] != prompt_id]
            return {"message": "Prompt deleted successfully"}

    raise HTTPException(status_code=404, detail="Prompt not found")


# =========== ADMIN-SPECIFIC ENDPOINTS ===========
@app.post("/admin/create_superuser/", response_model=AdminResponse)
def create_superuser(admin: AdminCreate, admin_token: str = None):
    # In a real app, validate admin token or other authentication method
    if not admin_token or admin_token != "super_secret_admin_token":
        raise HTTPException(status_code=403, detail="Not authorized to create admin users")

    # Force role to be admin
    admin.role = "admin"

    # Use the existing create_user function with admin privileges
    return create_user(admin, is_admin=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)