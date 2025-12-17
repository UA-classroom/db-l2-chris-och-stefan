# Add Pydantic schemas here that you'll use in your routes / endpoints
# Pydantic schemas are used to validate data that you receive, or to make sure that whatever data
# you send back to the client follows a certain structure
 
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- USERS ---
class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str
    language: str = "sv"

class UserUpdate(BaseModel):
    username: str
    email: str
    password_hash: str
    language: str
    is_verified: bool
    is_active: bool
    current_subscription_id: Optional[int] = None

class UserPatch(BaseModel):
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    language: Optional[str] = None

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    language: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    current_subscription_id: Optional[int] = None

# --- ROLES ---
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class RoleResponse(BaseModel):
    role_id: int
    name: str
    description: Optional[str] = None

# --- QUIZZES ---
class QuizCreate(BaseModel):
    name: str
    creation_method_id: Optional[int] = 1 # Default to manual
    creator_id: Optional[int]
    media_id: Optional[int] = None

class QuizUpdate(BaseModel):
    name: str
    creation_method_id: Optional[int]
    creator_id: Optional[int]
    media_id: Optional[int]

class QuizResponse(BaseModel):
    quiz_id: int
    name: str
    creation_method_id: Optional[int]
    creator_id: Optional[int]
    media_id: Optional[int]

# --- QUESTIONS ---
class QuestionCreate(BaseModel):
    quiz_id: int
    question_text: str
    question_type: str = "multiple_choice"
    time_limit: int = 30
    points: int = 1000
    sort_order: int = 1
    media_id: Optional[int] = None

class QuestionResponse(BaseModel):
    question_id: int
    quiz_id: int
    question_text: str
    question_type: str
    time_limit: int
    points: int
    sort_order: int
    media_id: Optional[int]

# --- ANSWERS ---
class AnswerCreate(BaseModel):
    question_id: int
    answer_text: str
    is_correct: bool
    sort_order: int = 1
    media_id: Optional[int] = None

class AnswerResponse(BaseModel):
    answer_id: int
    question_id: int
    answer_text: str
    is_correct: bool
    sort_order: int
    media_id: Optional[int]

# --- SESSIONS (GAME) ---
class SessionCreate(BaseModel):
    quiz_id: int
    host_id: int
    access_code: str

class SessionResponse(BaseModel):
    session_id: int
    quiz_id: int
    host_id: int
    access_code: str
    started_at: datetime
    ended_at: Optional[datetime]
    current_question_index: int

class ParticipantJoin(BaseModel):
    session_id: int
    user_id: Optional[int] = None
    nickname: str

class ParticipantAnswer(BaseModel):
    participant_id: int
    question_id: int
    chosen_answer_id: int
    is_correct: bool
    points_awarded: int

# --- ROLE UPDATES ---
class RoleUpdate(BaseModel):
    name: str
    description: Optional[str] = None

# --- QUESTION UPDATES ---
class QuestionUpdate(BaseModel):
    quiz_id: int
    question_text: str
    question_type: str
    time_limit: int
    points: int
    sort_order: int
    media_id: Optional[int] = None

# --- ANSWER UPDATES ---
class AnswerUpdate(BaseModel):
    question_id: int
    answer_text: str
    is_correct: bool
    sort_order: int
    media_id: Optional[int] = None

# --- PARTICIPANT SCORING ---
class ParticipantScoreUpdate(BaseModel):
    score: int