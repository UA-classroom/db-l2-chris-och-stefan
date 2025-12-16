import psycopg2
from psycopg2.extras import RealDictCursor

"""
This file is responsible for making database queries, which your fastapi endpoints/routes can use.
The reason we split them up is to avoid clutter in the endpoints, so that the endpoints might focus on other tasks 

- Try to return results with cursor.fetchall() or cursor.fetchone() when possible
- Make sure you always give the user response if something went right or wrong, sometimes 
you might need to use the RETURNING keyword to garantuee that something went right / wrong
e.g when making DELETE or UPDATE queries
- No need to use a class here
- Try to raise exceptions to make them more reusable and work a lot with returns
- You will need to decide which parameters each function should receive. All functions 
start with a connection parameter.
- Below, a few inspirational functions exist - feel free to completely ignore how they are structured
- E.g, if you decide to use psycopg3, you'd be able to directly use pydantic models with the cursor, these examples are however using psycopg2 and RealDictCursor
"""


# USERS
# __________________________________________________________________


def users_list(connection, is_active: bool | None = None):
    q = """
    SELECT user_id, username, email, language, is_verified, is_active, created_at, current_subscription_id
    FROM users
    """
    params = []
    if is_active is not None:
        q += " WHERE is_active = %s"
        params.append(is_active)
    q += " ORDER BY user_id DESC"

    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(q, params)
        return cur.fetchall()


def users_get(connection, user_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT user_id, username, email, language, is_verified, is_active, created_at, current_subscription_id
            FROM users
            WHERE user_id = %s
            """,
            (user_id,),
        )
        return cur.fetchone()


def users_create(
    connection, username: str, email: str, password_hash: str, language: str = "sv"
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, language)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id, username, email, language, is_verified, is_active, created_at, current_subscription_id
            """,
            (username, email, password_hash, language),
        )
        connection.commit()
        return cur.fetchone()


def users_update(
    connection,
    user_id: int,
    username: str,
    email: str,
    password_hash: str,
    language: str,
    is_verified: bool,
    is_active: bool,
    current_subscription_id: int | None,
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE users
            SET username=%s, email=%s, password_hash=%s, language=%s,
                is_verified=%s, is_active=%s, current_subscription_id=%s
            WHERE user_id=%s
            RETURNING user_id, username, email, language, is_verified, is_active, created_at, current_subscription_id
            """,
            (
                username,
                email,
                password_hash,
                language,
                is_verified,
                is_active,
                current_subscription_id,
                user_id,
            ),
        )
        return cur.fetchone()


def users_patch(
    connection, user_id: int, is_active=None, is_verified=None, language=None
):
    fields, vals = [], []
    if is_active is not None:
        fields.append("is_active=%s")
        vals.append(is_active)
    if is_verified is not None:
        fields.append("is_verified=%s")
        vals.append(is_verified)
    if language is not None:
        fields.append("language=%s")
        vals.append(language)

    if not fields:
        raise ValueError("No fields provided")

    vals.append(user_id)

    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            UPDATE users
            SET {", ".join(fields)}
            WHERE user_id=%s
            RETURNING user_id, username, email, language, is_verified, is_active, created_at, current_subscription_id
            """,
            tuple(vals),
        )
        return cur.fetchone()


def users_delete(connection, user_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        return cur.rowcount


def user_roles_list(connection, user_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT r.role_id, r.name, r.description
            FROM user_role ur
            JOIN role r ON r.role_id = ur.role_id
            WHERE ur.user_id = %s
            ORDER BY r.role_id
            """,
            (user_id,),
        )
        return cur.fetchall()


def user_roles_add(connection, user_id: int, role_id: int):
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO user_role (user_id, role_id) VALUES (%s, %s)",
            (user_id, role_id),
        )
        return {"user_id": user_id, "role_id": role_id}


def user_roles_remove(connection, user_id: int, role_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute(
            "DELETE FROM user_role WHERE user_id=%s AND role_id=%s",
            (user_id, role_id),
        )
        return cur.rowcount


# RBAC: ROLES & PERMISSIONS
# ___________________________________________________________________________
def roles_list(connection):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT role_id, name, description FROM role ORDER BY role_id")
        return cur.fetchall()


def roles_get(connection, role_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT role_id, name, description FROM role WHERE role_id=%s", (role_id,)
        )
        return cur.fetchone()


def roles_create(connection, name: str, description: str | None):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO role (name, description) VALUES (%s, %s) RETURNING role_id, name, description",
            (name, description),
        )
        return cur.fetchone()


def roles_update(connection, role_id: int, name: str, description: str | None):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE role SET name=%s, description=%s
            WHERE role_id=%s
            RETURNING role_id, name, description
            """,
            (name, description, role_id),
        )
        return cur.fetchone()


def roles_delete(connection, role_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute("DELETE FROM role WHERE role_id=%s", (role_id,))
        return cur.rowcount


def permissions_list(connection):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT permission_id, name, description FROM permission ORDER BY permission_id"
        )
        return cur.fetchall()


def permissions_get(connection, permission_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT permission_id, name, description FROM permission WHERE permission_id=%s",
            (permission_id,),
        )
        return cur.fetchone()


def permissions_create(connection, name: str, description: str | None):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO permission (name, description) VALUES (%s, %s) RETURNING permission_id, name, description",
            (name, description),
        )
        return cur.fetchone()


def permissions_update(
    connection, permission_id: int, name: str, description: str | None
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE permission SET name=%s, description=%s
            WHERE permission_id=%s
            RETURNING permission_id, name, description
            """,
            (name, description, permission_id),
        )
        return cur.fetchone()


def permissions_delete(connection, permission_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute("DELETE FROM permission WHERE permission_id=%s", (permission_id,))
        return cur.rowcount


def role_permissions_list(connection, role_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT p.permission_id, p.name, p.description
            FROM role_permission rp
            JOIN permission p ON p.permission_id = rp.permission_id
            WHERE rp.role_id = %s
            ORDER BY p.permission_id
            """,
            (role_id,),
        )
        return cur.fetchall()


def role_permissions_add(connection, role_id: int, permission_id: int):
    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO role_permission (role_id, permission_id) VALUES (%s, %s)",
            (role_id, permission_id),
        )
        return {"role_id": role_id, "permission_id": permission_id}


def role_permissions_remove(connection, role_id: int, permission_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute(
            "DELETE FROM role_permission WHERE role_id=%s AND permission_id=%s",
            (role_id, permission_id),
        )
        return cur.rowcount


# QUIZZES / QUESTIONS / ANSWERS
# ____________________________________________________________________________________________
def quizzes_list(connection, creator_id: int | None = None):
    q = "SELECT quiz_id, name, creation_method_id, creator_id, media_id FROM quiz"
    params = []
    if creator_id is not None:
        q += " WHERE creator_id=%s"
        params.append(creator_id)
    q += " ORDER BY quiz_id DESC"

    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(q, params)
        return cur.fetchall()


def quizzes_get(connection, quiz_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT quiz_id, name, creation_method_id, creator_id, media_id FROM quiz WHERE quiz_id=%s",
            (quiz_id,),
        )
        return cur.fetchone()


def quizzes_create(
    connection,
    name: str,
    creation_method_id: int | None,
    creator_id: int | None,
    media_id: int | None,
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO quiz (name, creation_method_id, creator_id, media_id)
            VALUES (%s, %s, %s, %s)
            RETURNING quiz_id, name, creation_method_id, creator_id, media_id
            """,
            (name, creation_method_id, creator_id, media_id),
        )
        return cur.fetchone()


def quizzes_update(
    connection,
    quiz_id: int,
    name: str,
    creation_method_id: int | None,
    creator_id: int | None,
    media_id: int | None,
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE quiz
            SET name=%s, creation_method_id=%s, creator_id=%s, media_id=%s
            WHERE quiz_id=%s
            RETURNING quiz_id, name, creation_method_id, creator_id, media_id
            """,
            (name, creation_method_id, creator_id, media_id, quiz_id),
        )
        return cur.fetchone()


def quizzes_delete(connection, quiz_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute("DELETE FROM quiz WHERE quiz_id=%s", (quiz_id,))
        return cur.rowcount


def questions_list_for_quiz(connection, quiz_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT question_id, quiz_id, question_text, question_type, time_limit, points, sort_order, media_id
            FROM quiz_question
            WHERE quiz_id=%s
            ORDER BY sort_order NULLS LAST, question_id
            """,
            (quiz_id,),
        )
        return cur.fetchall()


def questions_get(connection, question_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT question_id, quiz_id, question_text, question_type, time_limit, points, sort_order, media_id
            FROM quiz_question
            WHERE question_id=%s
            """,
            (question_id,),
        )
        return cur.fetchone()


def questions_create(
    connection,
    quiz_id: int,
    question_text,
    question_type,
    time_limit,
    points,
    sort_order,
    media_id,
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO quiz_question (quiz_id, question_text, question_type, time_limit, points, sort_order, media_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING question_id, quiz_id, question_text, question_type, time_limit, points, sort_order, media_id
            """,
            (
                quiz_id,
                question_text,
                question_type,
                time_limit,
                points,
                sort_order,
                media_id,
            ),
        )
        return cur.fetchone()


def questions_update(
    connection,
    question_id: int,
    quiz_id: int,
    question_text,
    question_type,
    time_limit,
    points,
    sort_order,
    media_id,
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE quiz_question
            SET quiz_id=%s, question_text=%s, question_type=%s, time_limit=%s,
                points=%s, sort_order=%s, media_id=%s
            WHERE question_id=%s
            RETURNING question_id, quiz_id, question_text, question_type, time_limit, points, sort_order, media_id
            """,
            (
                quiz_id,
                question_text,
                question_type,
                time_limit,
                points,
                sort_order,
                media_id,
                question_id,
            ),
        )
        return cur.fetchone()


def questions_delete(connection, question_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute("DELETE FROM quiz_question WHERE question_id=%s", (question_id,))
        return cur.rowcount


def answers_list_for_question(connection, question_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT answer_id, question_id, answer_text, is_correct, sort_order, media_id
            FROM quiz_answer
            WHERE question_id=%s
            ORDER BY sort_order NULLS LAST, answer_id
            """,
            (question_id,),
        )
        return cur.fetchall()


def answers_get(connection, answer_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT answer_id, question_id, answer_text, is_correct, sort_order, media_id
            FROM quiz_answer
            WHERE answer_id=%s
            """,
            (answer_id,),
        )
        return cur.fetchone()


def answers_create(
    connection, question_id: int, answer_text, is_correct, sort_order, media_id
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO quiz_answer (question_id, answer_text, is_correct, sort_order, media_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING answer_id, question_id, answer_text, is_correct, sort_order, media_id
            """,
            (question_id, answer_text, is_correct, sort_order, media_id),
        )
        return cur.fetchone()


def answers_update(
    connection,
    answer_id: int,
    question_id: int,
    answer_text,
    is_correct,
    sort_order,
    media_id,
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE quiz_answer
            SET question_id=%s, answer_text=%s, is_correct=%s, sort_order=%s, media_id=%s
            WHERE answer_id=%s
            RETURNING answer_id, question_id, answer_text, is_correct, sort_order, media_id
            """,
            (question_id, answer_text, is_correct, sort_order, media_id, answer_id),
        )
        return cur.fetchone()


def answers_delete(connection, answer_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute("DELETE FROM quiz_answer WHERE answer_id=%s", (answer_id,))
        return cur.rowcount


# SESSIONS / PARTICIPANTS / PARTICIPANT_ANSWER
# _______________________________________________________________________________________
def sessions_list(connection, quiz_id: int | None = None):
    q = """
    SELECT session_id, quiz_id, host_id, access_code, started_at, ended_at, current_question_index
    FROM game_session
    """
    params = []
    if quiz_id is not None:
        q += " WHERE quiz_id=%s"
        params.append(quiz_id)
    q += " ORDER BY session_id DESC"

    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(q, params)
        return cur.fetchall()


def sessions_get(connection, session_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT session_id, quiz_id, host_id, access_code, started_at, ended_at, current_question_index
            FROM game_session
            WHERE session_id=%s
            """,
            (session_id,),
        )
        return cur.fetchone()


def sessions_get_by_code(connection, access_code: str):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT session_id, quiz_id, host_id, access_code, started_at, ended_at, current_question_index
            FROM game_session
            WHERE access_code=%s
            """,
            (access_code,),
        )
        return cur.fetchone()


def sessions_create(
    connection, quiz_id: int | None, host_id: int | None, access_code: str
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO game_session (quiz_id, host_id, access_code, started_at, current_question_index)
            VALUES (%s, %s, %s, NOW(), 0)
            RETURNING session_id, quiz_id, host_id, access_code, started_at, ended_at, current_question_index
            """,
            (quiz_id, host_id, access_code),
        )
        return cur.fetchone()


def sessions_patch(
    connection, session_id: int, current_question_index=None, ended_at=None
):
    fields, vals = [], []
    if current_question_index is not None:
        fields.append("current_question_index=%s")
        vals.append(current_question_index)
    if ended_at is not None:
        fields.append("ended_at=%s")
        vals.append(ended_at)

    if not fields:
        raise ValueError("No fields provided")

    vals.append(session_id)

    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            UPDATE game_session
            SET {", ".join(fields)}
            WHERE session_id=%s
            RETURNING session_id, quiz_id, host_id, access_code, started_at, ended_at, current_question_index
            """,
            tuple(vals),
        )
        return cur.fetchone()


def sessions_next_question(connection, session_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE game_session
            SET current_question_index = COALESCE(current_question_index, 0) + 1
            WHERE session_id=%s
            RETURNING session_id, quiz_id, host_id, access_code, started_at, ended_at, current_question_index
            """,
            (session_id,),
        )
        return cur.fetchone()


def sessions_delete(connection, session_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute("DELETE FROM game_session WHERE session_id=%s", (session_id,))
        return cur.rowcount


def participants_list(connection, session_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT participant_id, session_id, user_id, nickname, joined_at, score
            FROM session_participant
            WHERE session_id=%s
            ORDER BY participant_id
            """,
            (session_id,),
        )
        return cur.fetchall()


def participants_join(
    connection, session_id: int, user_id: int | None, nickname: str | None
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO session_participant (session_id, user_id, nickname, joined_at, score)
            VALUES (%s, %s, %s, NOW(), 0)
            RETURNING participant_id, session_id, user_id, nickname, joined_at, score
            """,
            (session_id, user_id, nickname),
        )
        return cur.fetchone()


def participants_update_score(connection, participant_id: int, score: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            UPDATE session_participant
            SET score=%s
            WHERE participant_id=%s
            RETURNING participant_id, session_id, user_id, nickname, joined_at, score
            """,
            (score, participant_id),
        )
        return cur.fetchone()


def participants_delete(connection, participant_id: int) -> int:
    with connection.cursor() as cur:
        cur.execute(
            "DELETE FROM session_participant WHERE participant_id=%s", (participant_id,)
        )
        return cur.rowcount


def participant_answers_list(connection, participant_id: int):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, participant_id, question_id, chosen_answer_id, is_correct, points_awarded, answered_at
            FROM participant_answer
            WHERE participant_id=%s
            ORDER BY id
            """,
            (participant_id,),
        )
        return cur.fetchall()


def participant_answers_create(
    connection,
    participant_id: int,
    question_id: int,
    chosen_answer_id: int | None,
    is_correct: bool | None,
    points_awarded: int | None,
):
    with connection.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO participant_answer
                (participant_id, question_id, chosen_answer_id, is_correct, points_awarded, answered_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id, participant_id, question_id, chosen_answer_id, is_correct, points_awarded, answered_at
            """,
            (participant_id, question_id, chosen_answer_id, is_correct, points_awarded),
        )
        return cur.fetchone()
