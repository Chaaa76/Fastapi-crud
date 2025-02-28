from enum import Enum
from fastapi import FastAPI, HTTPException, Depends, Path
from typing import List, Dict, Optional
from pydantic import BaseModel


class ResidentStatus(str, Enum):
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    APPROVED = "approved"


class ResidentStatusUpdate(BaseModel):
    status: ResidentStatus

# In-memory storage for resident statuses
resident_statuses = {}

# Initialize FastAPI
app = FastAPI(title="Resident Status API")

@app.post("/resident/{resident_id}/status/")
def create_resident_status(
    resident_id: int = Path(..., description="The ID of the resident"),
    status_data: ResidentStatusUpdate = ...,
):
#create status
    resident_statuses[resident_id] = status_data.status
    return {"resident_id": resident_id, "status": status_data.status}

@app.get("/resident/{resident_id}/status/")
def get_resident_status(
    resident_id: int = Path(..., description="The ID of the resident")
):
    #get reesident stsatus
    if resident_id not in resident_statuses:
        raise HTTPException(status_code=404, detail="Resident status not found")
    return {"resident_id": resident_id, "status": resident_statuses[resident_id]}

@app.put("/resident/{resident_id}/status/")
def update_resident_status(
    resident_id: int = Path(..., description="The ID of the resident"),
    status_data: ResidentStatusUpdate = ...,
):
    #update resient status
    if resident_id not in resident_statuses:
        raise HTTPException(status_code=404, detail="Resident status not found")
    resident_statuses[resident_id] = status_data.status
    return {"resident_id": resident_id, "status": status_data.status}

@app.get("/resident/statuses/")
def get_all_resident_statuses():
    #get remianig statuses
    return [{"resident_id": rid, "status": status} for rid, status in resident_statuses.items()]