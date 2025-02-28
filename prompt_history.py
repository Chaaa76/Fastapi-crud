from fastapi import FastAPI, HTTPException, Path, Query, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


# PromptHistory model according to the UML
class PromptHistoryBase(BaseModel):
    id: Optional[int] = None
    title: str
    user_id: int
    prompt: str
    created_at: datetime = datetime.now()


class PromptHistoryCreate(BaseModel):
    title: str
    prompt: str


class PromptHistoryResponse(PromptHistoryBase):
    pass


# In-memory storage for prompt histories
prompt_histories = []
prompt_id_counter = 1

# Initialize FastAPI
app = FastAPI(title="Prompt History API")


@app.post("/resident/{user_id}/prompts/", response_model=PromptHistoryResponse)
def create_user_prompt(
        user_id: int = Path(..., description="The ID of the user"),
        prompt_data: PromptHistoryCreate = ...,
):
    #new promp history
    global prompt_id_counter

    new_prompt = PromptHistoryBase(
        id=prompt_id_counter,
        title=prompt_data.title,
        user_id=user_id,
        prompt=prompt_data.prompt,
        created_at=datetime.now()
    )

    prompt_dict = new_prompt.dict()
    prompt_histories.append(prompt_dict)
    prompt_id_counter += 1

    return prompt_dict


@app.get("/resident/{user_id}/prompts/", response_model=List[PromptHistoryResponse])
def get_user_prompts(
        user_id: int = Path(..., description="The ID of the user"),
):
    #get all prompt history
    user_prompts = [prompt for prompt in prompt_histories if prompt["user_id"] == user_id]
    return user_prompts


@app.get("/prompts/{prompt_id}", response_model=PromptHistoryResponse)
def get_prompt(
        prompt_id: int = Path(..., description="The ID of the prompt to retrieve"),
):
    #specific id
    for prompt in prompt_histories:
        if prompt["id"] == prompt_id:
            return prompt
    raise HTTPException(status_code=404, detail="Prompt not found")


@app.put("/prompts/{prompt_id}", response_model=PromptHistoryResponse)
def update_prompt(
        prompt_id: int = Path(..., description="The ID of the prompt to update"),
        prompt_data: PromptHistoryCreate = ...,
):
    #update
    for prompt in prompt_histories:
        if prompt["id"] == prompt_id:
            prompt["title"] = prompt_data.title
            prompt["prompt"] = prompt_data.prompt
            prompt["created_at"] = datetime.now()  # Update timestamp
            return prompt
    raise HTTPException(status_code=404, detail="Prompt not found")


@app.delete("/prompts/{prompt_id}")
def delete_prompt(
        prompt_id: int = Path(..., description="The ID of the prompt to delete"),
):
    #delete
    global prompt_histories
    for prompt in prompt_histories:
        if prompt["id"] == prompt_id:
            prompt_histories = [p for p in prompt_histories if p["id"] != prompt_id]
            return {"message": "Prompt deleted successfully"}
    raise HTTPException(status_code=404, detail="Prompt not found")


@app.get("/prompts/", response_model=List[PromptHistoryResponse])
def get_all_prompts():
    #get all promopts
    return prompt_histories