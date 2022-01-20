import logging
import sqlite3
import random
import string

def generate_alphanum_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string

create_tokens_table_cmd = """
CREATE TABLE IF NOT EXISTS admin_tokens(
  body TEXT NOT NULL
);
"""

create_token_cmd = """
INSERT INTO
  admin_tokens (body)
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


execute_query(create_connection("database.sqlite"), create_tokens_table_cmd)
token = generate_alphanum_random_string(16)
execute_query(create_connection("database.sqlite"), create_token_cmd % token)
print(f"Your admin token: {token}")
