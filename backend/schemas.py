from pydantic import BaseModel
from datetime import datetime
from typing import List

class SignupModel(BaseModel):
    username: str
    password: str
    role: str

class AssignmentModel(BaseModel):
    title: str
    description: str

class SubmissionOut(BaseModel):
    id: int
    assignment_id: int
    submitted_by: int
    file_path: str
    timestamp: datetime

    class Config:
        from_attributes = True
