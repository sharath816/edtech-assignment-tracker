from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import shutil, os

from database import SessionLocal, engine
from models import Base, User, Assignment, Submission
from schemas import SignupModel, AssignmentModel
from auth import get_password_hash, verify_password, create_access_token, get_user, get_current_user

# --- Initialize App ---
app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- File Upload Directory ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- DB Table Creation ---
Base.metadata.create_all(bind=engine)

# --- Dependency: get_db ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================
#         ROUTES
# ========================

@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

@app.post("/signup")
def signup(user: SignupModel):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == user.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        new_user = User(
            username=user.username,
            hashed_password=get_password_hash(user.password),
            role=user.role
        )
        db.add(new_user)
        db.commit()
        return {"message": "User registered successfully"}
    finally:
        db.close()

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    try:
        user = get_user(db, form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        token = create_access_token({"sub": user.username})
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role
        }
    finally:
        db.close()

@app.post("/assignments")
def create_assignment(assignment: AssignmentModel, current_user: User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")
    db = SessionLocal()
    try:
        new_assignment = Assignment(
            title=assignment.title,
            description=assignment.description,
            created_by=current_user.id
        )
        db.add(new_assignment)
        db.commit()
        return {"message": "Assignment created successfully"}
    finally:
        db.close()

@app.get("/assignments")
def get_assignments(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        return db.query(Assignment).all()
    finally:
        db.close()

@app.delete("/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can delete assignments.")

    db.delete(assignment)
    db.commit()

    return {"message": "Assignment deleted successfully."}

@app.get("/my-assignments")
def get_my_assignments(current_user: User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view their assignments")
    
    db = SessionLocal()
    try:
        assignments = db.query(Assignment).filter(Assignment.created_by == current_user.id).all()
        return assignments
    finally:
        db.close()

@app.post("/submit")
def submit_assignment(
    assignment_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")

    filename = f"{UPLOAD_DIR}/{datetime.utcnow().timestamp()}_{file.filename}"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db = SessionLocal()
    try:
        submission = Submission(
            assignment_id=assignment_id,
            submitted_by=current_user.id,
            file_path=filename
        )
        db.add(submission)
        db.commit()
        return {"message": "Assignment submitted successfully"}
    finally:
        db.close()

@app.get("/submissions/{assignment_id}")
def view_submissions(assignment_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view submissions")

    db = SessionLocal()
    try:
        submissions = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
        result = []
        for sub in submissions:
            student = db.query(User).filter(User.id == sub.submitted_by).first()
            result.append({
                "submission_id": sub.id,
                "assignment_id": sub.assignment_id,
                "student_id": sub.submitted_by,
                "student_username": student.username if student else "Unknown",
                "file_path": sub.file_path
            })
        return result
    finally:
        db.close()

@app.get("/my-submissions")
def my_submissions(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their submissions")

    db = SessionLocal()
    try:
        submissions = db.query(Submission).filter(Submission.submitted_by == current_user.id).all()
        result = []
        for sub in submissions:
            assignment = db.query(Assignment).filter(Assignment.id == sub.assignment_id).first()
            result.append({
                "submission_id": sub.id,
                "assignment_title": assignment.title if assignment else "Unknown",
                "file_path": sub.file_path,
                "timestamp": sub.timestamp
            })
        return result
    finally:
        db.close()

@app.get("/download/{submission_id}")
def download(submission_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        sub = db.query(Submission).filter(Submission.id == submission_id).first()
        if not sub:
            raise HTTPException(status_code=404, detail="Submission not found")
        return FileResponse(sub.file_path)
    finally:
        db.close()
