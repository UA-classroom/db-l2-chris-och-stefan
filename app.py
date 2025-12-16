import os

import psycopg2
from db_setup import get_connection
from fastapi import FastAPI, HTTPException

app = FastAPI()

"""
ADD ENDPOINTS FOR FASTAPI HERE
Make sure to do the following:
- Use the correct HTTP method (e.g get, post, put, delete)
- Use correct STATUS CODES, e.g 200, 400, 401 etc. when returning a result to the user
- Use pydantic models whenever you receive user data and need to validate the structure and data types (VG)
This means you need some error handling that determine what should be returned to the user
Read more: https://www.geeksforgeeks.org/10-most-common-http-status-codes/
- Use correct URL paths the resource, e.g some endpoints should be located at the exact same URL, 
but will have different HTTP-verbs.
"""


# INSPIRATION FOR A LIST-ENDPOINT - Not necessary to use pydantic models, but we could to ascertain that we return the correct values
# @app.get("/items/")
# def read_items():
#     con = get_connection()
#     items = get_items(con)
#     return {"items": items}


# INSPIRATION FOR A POST-ENDPOINT, uses a pydantic model to validate
# @app.post("/validation_items/")
# def create_item_validation(item: ItemCreate):
#     con = get_connection()
#     item_id = add_item_validation(con, item)
#     return {"item_id": item_id}


# IMPLEMENT THE ACTUAL ENDPOINTS! Feel free to remove

from fastapi import FastAPI, HTTPException, Depends
from typing import List
import schemas
import db
# Import get_connection from YOUR db_setup file
from db_setup import get_connection 

app = FastAPI()

# --- DEPENDENCY ---
# This opens a connection for a request, yields it to the endpoint,
# and closes it automatically when the request is done.
def get_db_conn():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

@app.get("/")
def root():
    return {"message": "Kahoot Clone API"}

# ==========================================
# GROUP: GET (Read Data)
# ==========================================

@app.get("/users/", tags=["GET"], response_model=List[schemas.UserResponse])
def get_users(active: bool = None, conn = Depends(get_db_conn)):
    return db.users_list(conn, is_active=active)

@app.get("/users/{user_id}", tags=["GET"], response_model=schemas.UserResponse)
def get_user(user_id: int, conn = Depends(get_db_conn)):
    user = db.users_get(conn, user_id)
    if not user: raise HTTPException(404, "User not found")
    return user

@app.get("/roles/", tags=["GET"], response_model=List[schemas.RoleResponse])
def get_roles(conn = Depends(get_db_conn)):
    return db.roles_list(conn)

@app.get("/quizzes/", tags=["GET"], response_model=List[schemas.QuizResponse])
def get_quizzes(creator_id: int = None, conn = Depends(get_db_conn)):
    return db.quizzes_list(conn, creator_id)

@app.get("/quizzes/{quiz_id}", tags=["GET"], response_model=schemas.QuizResponse)
def get_quiz(quiz_id: int, conn = Depends(get_db_conn)):
    quiz = db.quizzes_get(conn, quiz_id)
    if not quiz: raise HTTPException(404, "Quiz not found")
    return quiz

@app.get("/quizzes/{quiz_id}/questions", tags=["GET"], response_model=List[schemas.QuestionResponse])
def get_questions(quiz_id: int, conn = Depends(get_db_conn)):
    return db.questions_list_for_quiz(conn, quiz_id)

@app.get("/questions/{question_id}/answers", tags=["GET"], response_model=List[schemas.AnswerResponse])
def get_answers(question_id: int, conn = Depends(get_db_conn)):
    return db.answers_list_for_question(conn, question_id)

@app.get("/sessions/{access_code}", tags=["GET"], response_model=schemas.SessionResponse)
def get_session_by_code(access_code: str, conn = Depends(get_db_conn)):
    session = db.sessions_get_by_code(conn, access_code)
    if not session: raise HTTPException(404, "Session not found")
    return session


# ==========================================
# GROUP: POST (Create Data)
# ==========================================

@app.post("/users/", tags=["POST"], response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, conn = Depends(get_db_conn)):
    return db.users_create(conn, user.username, user.email, user.password_hash, user.language)

@app.post("/roles/", tags=["POST"], response_model=schemas.RoleResponse)
def create_role(role: schemas.RoleCreate, conn = Depends(get_db_conn)):
    return db.roles_create(conn, role.name, role.description)

@app.post("/quizzes/", tags=["POST"], response_model=schemas.QuizResponse)
def create_quiz(quiz: schemas.QuizCreate, conn = Depends(get_db_conn)):
    return db.quizzes_create(conn, quiz.name, quiz.creation_method_id, quiz.creator_id, quiz.media_id)

@app.post("/questions/", tags=["POST"], response_model=schemas.QuestionResponse)
def create_question(q: schemas.QuestionCreate, conn = Depends(get_db_conn)):
    return db.questions_create(conn, q.quiz_id, q.question_text, q.question_type, q.time_limit, q.points, q.sort_order, q.media_id)

@app.post("/answers/", tags=["POST"], response_model=schemas.AnswerResponse)
def create_answer(a: schemas.AnswerCreate, conn = Depends(get_db_conn)):
    return db.answers_create(conn, a.question_id, a.answer_text, a.is_correct, a.sort_order, a.media_id)

@app.post("/sessions/", tags=["POST"], response_model=schemas.SessionResponse)
def start_session(s: schemas.SessionCreate, conn = Depends(get_db_conn)):
    return db.sessions_create(conn, s.quiz_id, s.host_id, s.access_code)

@app.post("/sessions/join", tags=["POST"])
def join_session(p: schemas.ParticipantJoin, conn = Depends(get_db_conn)):
    return db.participants_join(conn, p.session_id, p.user_id, p.nickname)

@app.post("/sessions/submit-answer", tags=["POST"])
def submit_answer(ans: schemas.ParticipantAnswer, conn = Depends(get_db_conn)):
    return db.participant_answers_create(conn, ans.participant_id, ans.question_id, ans.chosen_answer_id, ans.is_correct, ans.points_awarded)


# ==========================================
# GROUP: PUT (Update Everything)
# ==========================================

@app.put("/users/{user_id}", tags=["PUT"], response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserUpdate, conn = Depends(get_db_conn)):
    updated = db.users_update(conn, user_id, user.username, user.email, user.password_hash, user.language, user.is_verified, user.is_active, user.current_subscription_id)
    if not updated: raise HTTPException(404, "User not found")
    return updated

@app.put("/roles/{role_id}", tags=["PUT"], response_model=schemas.RoleResponse)
def update_role(role_id: int, role: schemas.RoleUpdate, conn = Depends(get_db_conn)):
    updated = db.roles_update(conn, role_id, role.name, role.description)
    if not updated: raise HTTPException(404, "Role not found")
    return updated

@app.put("/questions/{question_id}", tags=["PUT"], response_model=schemas.QuestionResponse)
def update_question(question_id: int, q: schemas.QuestionUpdate, conn = Depends(get_db_conn)):
    updated = db.questions_update(conn, question_id, q.quiz_id, q.question_text, q.question_type, q.time_limit, q.points, q.sort_order, q.media_id)
    if not updated: raise HTTPException(404, "Question not found")
    return updated

@app.put("/answers/{answer_id}", tags=["PUT"], response_model=schemas.AnswerResponse)
def update_answer(answer_id: int, a: schemas.AnswerUpdate, conn = Depends(get_db_conn)):
    updated = db.answers_update(conn, answer_id, a.question_id, a.answer_text, a.is_correct, a.sort_order, a.media_id)
    if not updated: raise HTTPException(404, "Answer not found")
    return updated

@app.put("/participants/{participant_id}/score", tags=["PUT"])
def update_participant_score(participant_id: int, data: schemas.ParticipantScoreUpdate, conn = Depends(get_db_conn)):
    updated = db.participants_update_score(conn, participant_id, data.score)
    if not updated: raise HTTPException(404, "Participant not found")
    return updated


# ==========================================
# GROUP: PATCH (Partial Update)
# ==========================================

@app.patch("/users/{user_id}", tags=["PATCH"], response_model=schemas.UserResponse)
def patch_user(user_id: int, patch: schemas.UserPatch, conn = Depends(get_db_conn)):
    updated = db.users_patch(conn, user_id, patch.is_active, patch.is_verified, patch.language)
    if not updated: raise HTTPException(404, "User not found")
    return updated


# ==========================================
# GROUP: DELETE (Remove)
# ==========================================

@app.delete("/users/{user_id}", tags=["DELETE"])
def delete_user(user_id: int, conn = Depends(get_db_conn)):
    if db.users_delete(conn, user_id) == 0: raise HTTPException(404, "User not found")
    return {"message": "User deleted"}

@app.delete("/roles/{role_id}", tags=["DELETE"])
def delete_role(role_id: int, conn = Depends(get_db_conn)):
    if db.roles_delete(conn, role_id) == 0: raise HTTPException(404, "Role not found")
    return {"message": "Role deleted"}

@app.delete("/sessions/{session_id}", tags=["DELETE"])
def delete_session(session_id: int, conn = Depends(get_db_conn)):
    if db.sessions_delete(conn, session_id) == 0: raise HTTPException(404, "Session not found")
    return {"message": "Session deleted"}

@app.delete("/participants/{participant_id}", tags=["DELETE"])
def delete_participant(participant_id: int, conn = Depends(get_db_conn)):
    if db.participants_delete(conn, participant_id) == 0: raise HTTPException(404, "Participant not found")
    return {"message": "Participant removed"}

@app.delete("/answers/{answer_id}", tags=["DELETE"])
def delete_answer(answer_id: int, conn = Depends(get_db_conn)):
    if db.answers_delete(conn, answer_id) == 0: raise HTTPException(404, "Answer not found")
    return {"message": "Answer deleted"}