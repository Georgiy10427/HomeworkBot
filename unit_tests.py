import unittest
import aiohttp
from unittest import IsolatedAsyncioTestCase
import config
from aiogram import Bot
import mainBot
import dbHandle

connection = dbHandle.Connect("database.db")

key = "#всёдз за 30 апреля"
all_homework = """#всёдз за 30 апреля
Математика: Задание на 3.05: номера с 801 по 805 - первый столбик везде. + Учить параграф 4.6
Литература: читать все подвиги Геракла
Биология: ничего, предыдущее дз - параграф 51 - учить первые 2-3 царства.)"""

class TestDatabase(IsolatedAsyncioTestCase):
    async def test_db(self):
        #Тестирование подписок
        dbHandle.Subscribe(connection, 1111) #Подписываем тестового пользователя
        self.assertEqual(dbHandle.IsSubscriber(connection, 1111), True) #Проверяем подписан ли он?
        dbHandle.Unsubscribe(connection, 1111) #Отписываем тестового пользователя  
        self.assertEqual(dbHandle.IsSubscriber(connection, 1111), False) #Проверяем, отписался ли он?
        #Тестирование поиска и хранения постов
        print("Test database...")
        dbHandle.AddPost(connection, "34785873895!_+_^&*#&$(*#&(&$@#(*&&$(*_QWERTYYUIOP{}ASDFGHJKL:|ZXCVBNM<>?") #Добавляем тестовый пост
        self.assertEqual(dbHandle.SelectFromKey(connection, "*#&$")[-1][1], "34785873895!_+_^&*#&$(*#&(&$@#(*&&$(*_QWERTYYUIOP{}ASDFGHJKL:|ZXCVBNM<>?") #Ищем тестовый пост и сверяем с образцом
        dbHandle.DeleteFromKey(connection, "*#&$") #Удаляем тестовый пост
        self.assertEqual(dbHandle.SelectFromKey(connection, "*#&$"), []) #Проверяем удалился ли он
        print("Success test database.")

class TestBot(IsolatedAsyncioTestCase):
    async def test_bot_auth(self):
        print("Test connect to the bot.")
        #Проверяем соединение с ботом
        bot = Bot(token=config.API_TOKEN)
        bot._session = aiohttp.ClientSession()
        bot_info = await bot.get_me()
        await bot._session.close()
        try:
            self.assertEqual(bot_info["username"], "AllHomework_bot")
        except:
            self.assertEqual(bot_info["username"], "AllHomeworkYbot")
        print("Success test connect to the bot. Bot name: " + bot_info["username"])

class TestService(IsolatedAsyncioTestCase):
    async def test_get_subjects(self):
        #Проверяем поиск заданий
        subject = mainBot.get_subject("Русский язык:")
        self.assertEqual(type(subject), str)
    async def test_cut_subjects(self):
        #Проверяем корректность отделения задания от остальных 
        print("Test cut_subject function...")
        cut = mainBot.cut_subject("Математика:", all_homework)
        for s in mainBot.subjects_names:
            if s != "Математика":
                self.assertEqual(s in cut, False)
            else:
                self.assertEqual(s in cut, True)
        print("Test cut_subject function is success.")

if __name__ == '__main__':
    unittest.main()