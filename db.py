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
