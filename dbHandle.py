import logging
import aiosqlite

# SQL commands:
create_posts_table_cmd = """
CREATE TABLE IF NOT EXISTS posts(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  body TEXT NOT NULL
);
"""
create_subscribers_table_cmd = """
CREATE TABLE IF NOT EXISTS subscribers(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  USER_ID TEXT NOT NULL
);
"""
create_posts_cmd = """
INSERT INTO
  posts (body)
VALUES
  ('%s');
"""

add_subscriber = """
INSERT INTO
  subscribers (USER_ID)
VALUES
  ('%s');
"""


def get_url():
    return "database.sqlite"


async def execute_query(filename, query):
    async with aiosqlite.connect(filename) as db:
        try:
            await db.execute(query)
            await db.commit()
        except Exception as e:
            logging.error(f"The error occurred: {e}")


async def execute_read_query(filename, query):
    async with aiosqlite.connect(filename) as db:
        try:
            async with db.execute(query) as cursor:
                return await cursor.fetchall()
        except Exception as e:
            logging.error(f"The error occurred: {e}")

# Replace "connection" to "filename" everything


async def add_post(filename, text):
    await execute_query(filename, create_posts_cmd % text)


async def create_posts(connection):
    await execute_query(connection, create_posts_table_cmd)


async def select_from_key(connection, key):
    query_value = await execute_read_query(connection,
                                     f"SELECT * FROM posts WHERE body LIKE '%{key}%';")
    return query_value


async def select_from_id(connection, note_id):
    query_value = await execute_read_query(connection,
                                     f"SELECT * FROM posts WHERE id = {note_id}")
    return query_value


async def update_from_key(connection, old_body, new_body):
    await execute_query(connection,
                  f"UPDATE posts SET body = '{new_body}' WHERE body LIKE '%{old_body}%';")


async def delete_from_key(connection, key):
    await execute_query(connection, f"DELETE FROM posts WHERE body LIKE '%{key}%';")


async def delete_from_id(connection, note_id):
    await execute_query(connection, f"DELETE FROM posts WHERE id = {note_id}")


async def delete_all_labels(connection):
    await execute_query(connection, "DELETE FROM posts")


async def create_subscribers(connection):
    await execute_query(connection, create_subscribers_table_cmd)


async def subscribe(connection, user_id):
    await execute_query(connection, add_subscriber % user_id)


async def unsubscribe(connection, user_id):
    await execute_query(connection, f"DELETE FROM subscribers WHERE USER_ID = {user_id}")


async def is_subscriber(connection, user_id):
    query_value = await execute_read_query(connection,
                                     f"SELECT * FROM subscribers WHERE USER_ID = {user_id}")
    if len(query_value) == 0:
        return False
    else:
        return True


async def get_subscribers(connection):
    query_value = await execute_read_query(connection, "SELECT * from subscribers")
    return query_value


async def get_task_where_id_less(connection, id: int, subject: str):
    query = f"SELECT * FROM posts WHERE body LIKE '%{subject}%' AND id < {id}"
    return await execute_read_query(connection, query)
