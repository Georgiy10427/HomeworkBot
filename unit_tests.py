import unittest
import aiohttp
from unittest import IsolatedAsyncioTestCase
import config
from aiogram import Bot
import mainBot
import dbHandle
import sqlite3

connection = sqlite3.connect("database.sqlite")

key = "#всёдз за 30 апреля"
all_homework = """#всёдз за 30 апреля
Математика: Задание на 3.05: номера с 801 по 805 - первый столбик везде. + Учить параграф 4.6
Литература: читать все подвиги Геракла
Биология: ничего, предыдущее дз - параграф 51 - учить первые 2-3 царства.)"""


class TestDatabase(IsolatedAsyncioTestCase):
    async def test_db(self):
        dbHandle.subscribe(connection, 1111)
        self.assertEqual(dbHandle.is_subscriber(connection, 1111), True)
        dbHandle.unsubscribe(connection, 1111)
        self.assertEqual(dbHandle.is_subscriber(connection, 1111), False)
        print("Test database...")
        dbHandle.add_post(connection, "34785873895!_+_^&*#&$(*#&(&$@#(*&&$(*_QWERTYYUIOP{}ASDFGHJKL:|ZXCVBNM<>?")
        self.assertEqual(dbHandle.select_from_key(connection, "*#&$")[-1][1], "34785873895!_+_^&*#&$(*#&(&$@#(*&&$(*_QWERTYYUIOP{}ASDFGHJKL:|ZXCVBNM<>?")
        dbHandle.delete_from_key(connection, "*#&$")
        self.assertEqual(dbHandle.select_from_key(connection, "*#&$"), [])
        print("Success test database.")


class TestBot(IsolatedAsyncioTestCase):
    async def test_bot_auth(self):
        bot = Bot(token=config.API_TOKEN)
        bot._session = aiohttp.ClientSession()
        bot_info = await bot.get_me()
        await bot._session.close()
        try:
            self.assertEqual(bot_info["username"], "AllHomework_bot")
        except:
            self.assertEqual(bot_info["username"], "AllHomeworkYbot")
        print("Success test connect to the bot. Bot name: " + bot_info["username"])

    async def test_get_subjects(self):
        subject = mainBot.get_subject("Русский язык:")
        self.assertEqual(type(subject), str)

    async def test_cut_subjects(self):
        print("Test cut_subject function...")
        cut = mainBot.cut_subject("Математика:", all_homework)
        for s in mainBot.subjects_names:
            if s != "Математика":
                self.assertEqual(s in cut, False)
            else:
                self.assertEqual(s in cut, True)
        print("Test cut_subject function is success.")


#class GdzTest(IsolatedAsyncioTestCase):
#    async def test_complete(self):
#


if __name__ == '__main__':
    unittest.main()