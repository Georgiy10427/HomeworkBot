import logging
import typing
import aiosqlite


create_posts_table_cmd: str = """
CREATE TABLE IF NOT EXISTS posts(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  body TEXT NOT NULL
);
"""
create_subscribers_table_cmd: str = """
CREATE TABLE IF NOT EXISTS subscribers(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  USER_ID TEXT NOT NULL
);
"""
create_posts_cmd: str = """
INSERT INTO
  posts (body)
VALUES
  ('%s');
"""

add_subscriber: str = """
INSERT INTO
  subscribers (USER_ID)
VALUES
  ('%s');
"""


def get_url() -> str:
    return "database.sqlite"


async def execute_query(filename: str, query: str) -> None:
    async with aiosqlite.connect(filename) as db:
        try:
            await db.execute(query)
            await db.commit()
        except Exception as e:
            logging.error(f"The error occurred: {e}")


async def execute_read_query(filename: str, query: str) -> list:
    async with aiosqlite.connect(filename) as db:
        try:
            async with db.execute(query) as cursor:
                return await cursor.fetchall()
        except Exception as e:
            logging.error(f"The error occurred: {e}")


async def create_tables() -> None:
    await create_posts(get_url())
    await create_subscribers(get_url())


async def add_post(filename: str, text: str) -> None:
    await execute_query(filename, create_posts_cmd % text)


async def create_posts(filename: str) -> None:
    await execute_query(filename, create_posts_table_cmd)


async def select_from_key(filename: str, key: str) -> list:
    query_value = await execute_read_query(filename,
                                           f"SELECT * FROM posts WHERE body LIKE '%{key}%';")
    return query_value


async def select_from_id(filename: str, note_id: typing.Union[int, str]) -> list:
    query_value = await execute_read_query(filename,
                                           f"SELECT * FROM posts WHERE id = {note_id}")
    return query_value


async def update_from_key(filename: str, old_body: str, new_body: str) -> None:
    await execute_query(filename,
                        f"UPDATE posts SET body = '{new_body}' WHERE body LIKE '%{old_body}%';")


async def delete_from_key(filename: str, key: str) -> None:
    await execute_query(filename, f"DELETE FROM posts WHERE body LIKE '%{key}%';")


async def delete_from_id(filename: str, note_id: typing.Union[str, int]) -> None:
    await execute_query(filename, f"DELETE FROM posts WHERE id = {note_id}")


async def delete_all_labels(filename: str) -> None:
    await execute_query(filename, "DELETE FROM posts")


async def create_subscribers(filename: str) -> None:
    await execute_query(filename, create_subscribers_table_cmd)


async def subscribe(filename: str, user_id: typing.Union[str, int]) -> None:
    await execute_query(filename, add_subscriber % user_id)


async def unsubscribe(filename: str, user_id: typing.Union[str, int]) -> None:
    await execute_query(filename, f"DELETE FROM subscribers WHERE USER_ID = {user_id}")


async def is_subscriber(filename: str, user_id: typing.Union[str, int]) -> bool:
    query_value = await execute_read_query(filename,
                                           f"SELECT * FROM subscribers WHERE USER_ID = {user_id}")
    if len(query_value) == 0:
        return False
    else:
        return True


async def get_subscribers(filename: str) -> list:
    query_value = await execute_read_query(filename, "SELECT * from subscribers")
    return query_value


async def get_task_where_id_less(filename: str, note_id: typing.Union[int, str], subject: str) -> list:
    query = f"SELECT * FROM posts WHERE body LIKE '%{subject}%' AND id < {note_id}"
    return await execute_read_query(filename, query)
