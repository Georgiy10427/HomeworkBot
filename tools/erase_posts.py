import dbHandle as db
import logging

check = input("Would you like to DELETE ALL YOUR PUBLICATIONS? Enter YES: ")
if check != "YES":
	exit(0)


second_check = input("Really? y/n: ")
if second_check != "y":
	exit(0)


logging.warning("Deleting all posts...")
connection = db.create_connection("database.db")
db.delete_all_labels(connection)
logging.info("Ok.")
