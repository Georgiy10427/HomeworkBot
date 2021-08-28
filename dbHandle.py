import logging
import sqlite3

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


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        logging.info("Connection to SQLite DB successful")
    except Exception as e:
        logging.error(f"The error occurred: {e}")
    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        logging.info("Query executed successfully")
    except Exception as e:
        logging.error(f"The error occurred: {e}")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        logging.error(f"The error occurred: {e}")


def add_post(connection, text):
    execute_query(connection, create_posts_cmd % text)


def create_posts(connection):
    execute_query(connection, create_posts_table_cmd)


def connect(filename):
    return create_connection(filename)


def select_from_key(connection, key):
    query_value = execute_read_query(connection,
                                     f"SELECT * FROM posts WHERE body LIKE '%{key}%';")
    return query_value


def select_from_id(connection, note_id):
    query_value = execute_read_query(connection,
                                     f"SELECT * FROM posts WHERE id = {note_id}")
    return query_value


def update_from_key(connection, old_body, new_body):
    execute_query(connection,
                  f"UPDATE posts SET body = '{new_body}' WHERE body LIKE '%{old_body}%';")


def delete_from_key(connection, key):
    execute_query(connection, f"DELETE FROM posts WHERE body LIKE '%{key}%';")


def delete_from_id(connection, note_id):
    execute_query(connection, f"DELETE FROM posts WHERE id = {note_id}")


def delete_all_labels(connection):
    execute_query(connection, "DELETE FROM posts")


def create_subscribers(connection):
    execute_query(connection, create_subscribers_table_cmd)


def subscribe(connection, user_id):
    execute_query(connection, add_subscriber % user_id)


def unsubscribe(connection, user_id):
    execute_query(connection, f"DELETE FROM subscribers WHERE USER_ID = {user_id}")


def is_subscriber(connection, user_id):
    query_value = execute_read_query(connection, f"SELECT * FROM subscribers WHERE USER_ID = {user_id}")
    if len(query_value) == 0:
        return False
    else:
        return True


def get_subscribers(connection):
    query_value = execute_read_query(connection, "SELECT * from subscribers")
    return query_value
