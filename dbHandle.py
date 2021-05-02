import sqlite3
import asyncio
#Commands:
create_posts_table = """
CREATE TABLE IF NOT EXISTS posts(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  body TEXT NOT NULL
);
"""
create_subscribers_table = """
CREATE TABLE IF NOT EXISTS subscribers(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  USER_ID TEXT NOT NULL
);
"""
create_posts = """
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
        print("Connection to SQLite DB successful")
    except:
        print("The error occurred")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except:
        print("The error occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except:
        print("The error occurred")

def AddPost(connection, text):
    execute_query(connection, create_posts % text)

def CreatePostsTable(connection):
    execute_query(connection, create_posts_table)

def Connect(filename):
    return create_connection(filename)

def SelectFromKey(connection, key):
    QueryValue = execute_read_query(connection,
                       "SELECT * FROM posts WHERE body LIKE '%" + str(key) + "%';")
    return QueryValue

def SelectFromId(connection, id):
    QueryValue = execute_read_query(connection,
                       "SELECT * FROM posts WHERE id = " + str(id))
    return QueryValue

def UpdateFromKey(connection, old_body, new_body):
    execute_query(connection, "UPDATE posts SET body = '" + str(new_body) + "' WHERE body LIKE '%" + str(old_body) + "%';")

def DeleteFromKey(connection, key):
    execute_query(connection, "DELETE FROM posts WHERE body LIKE '%" + str(key) + "%';")

def DeleteFromId(connection, id):
    execute_query(connection, "DELETE FROM posts WHERE id = " + str(id))

def DeleteAllLabels(connection):
    execute_query(connection, "DELETE FROM posts")

def CreateSubscribersTable(connection):
    execute_query(connection, create_subscribers_table)

def Subscribe(connection, USER_ID):
    execute_query(connection, add_subscriber % USER_ID)

def Unsubscribe(connection, USER_ID):
    execute_query(connection, "DELETE FROM subscribers WHERE USER_ID = " + str(USER_ID))

def IsSubscriber(connection, USER_ID):
    QueryValue = execute_read_query(connection, "SELECT * FROM subscribers WHERE USER_ID = " + str(USER_ID))
    if len(QueryValue) == 0:
        return False
    else:
        return True
        
def GetSubscribers(connection):
    QueryValue = execute_read_query(connection, "SELECT * from subscribers")
    return QueryValue