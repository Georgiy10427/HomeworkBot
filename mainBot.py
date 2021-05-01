import config
import logging
import asyncio
import dbHandle
from datetime import datetime
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
#Выше импорт необходимых модулей для работы бота

# задаем уровень логов
logging.basicConfig(level=logging.DEBUG)

# инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

#Список всех предметов для парсера
subjects_names = ['Русский язык', 'Математика',
                  'ИЗО', 'Обществознание',
                  'Английский язык',
                  'Всеобщая история', 'История России',
                  'Музыка', 'Биология', 'География', "Технология",
                  "Информатика", "Литература", "История россии", "Всеобщая История"
                 ]
aboutMSG = """
Бот призван помочь вам в поиске нужного домашнего задания. Сделан с акцентом на простоту и удобство)\nПрограмма полностью открыта.
Github: https://github.com/Georgiy10427/HomeworkBot
"""

#Кнопки с названиями пердметов
Russian = InlineKeyboardButton('Русский язык', callback_data='0')
Math = InlineKeyboardButton('Математика', callback_data='1')
Painting = InlineKeyboardButton('ИЗО', callback_data='2')
English = InlineKeyboardButton('Английский язык', callback_data='3')
History = InlineKeyboardButton('Всеобщая история', callback_data='4')
RussianHistory = InlineKeyboardButton('История России', callback_data='5')
Music = InlineKeyboardButton('Музыка', callback_data='6')
Bio = InlineKeyboardButton('Биология', callback_data='7')
Geography = InlineKeyboardButton('География', callback_data='8')
SocialScience = InlineKeyboardButton('Обществознание', callback_data='9')
Technology = InlineKeyboardButton('Технология', callback_data='10')
ComputerScience = InlineKeyboardButton('Информатика', callback_data='11')
Literature = InlineKeyboardButton('Литература', callback_data='12')

#Создаём клавиатуру, добавляя в неё выше объявленные кнопки 
keyboard = InlineKeyboardMarkup(row_width=2) \
        .row(Russian, Math, Painting) \
        .row(Literature, English).row(History, RussianHistory) \
        .row(Music, Bio) \
        .row(Geography, Technology) \
        .row(ComputerScience, SocialScience) 

MessageButtons = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Вернуться в меню', callback_data='back'),
    InlineKeyboardButton('Скрыть', callback_data='delete')
    )

#Подключаемся к БД (базе данных)
connection = dbHandle.Connect("database.db")
dbHandle.CreateTable(connection)

#Обработчик команды /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer_sticker("CAACAgIAAxkBAAEBO5VgiprjZ-LcWQABw12tF2wzdlqxoyIAAt4AA_R7GQABvYXvbvfFzj0fBA")
    await message.reply("Привет! Пожалуйста выбери нужный тебе предмет.", reply_markup=keyboard)

#Обработчик команды /about
@dp.message_handler(commands=['about'])
async def process_about_command(message: types.Message):
    await message.reply(aboutMSG)

#Обработчик других текстовых команд
@dp.message_handler()
async def answer(message: types.Message):
    command = message.text
    search_request = ""
    if message.from_user.id == config.owner_id and "/" in command:
        if "/add" in command:
            dbHandle.AddPost(connection, message.text.replace("/add ", ""))
            await message.reply("Добавлено!")
        elif "/update" in command:
            pass
        elif "/delete" in command:
            post = dbHandle.SelectFromKey(connection, message.text.replace("/delete ", ""))
            dbHandle.DeleteFromKey(connection, message.text.replace("/delete ", ""))
            try:
                await message.reply("Удалено. Удалённый пост: \n" + post[-1][1])
            except:
                await message.reply("Возникла ошибка :( \nВозможно, данная публикация не существует ¯\\_(ツ)_/¯")
    else:
        for subject in subjects_names:
            if subject in command:
                search_request = subject
                break
        if (search_request != ""): await message.reply(get_subject(search_request))
        else:
            await message.reply("Кажется, я не смогу тебе помочь")
            await message.answer_sticker("CAACAgIAAxkBAAEBOzxgikgyP2ZGA-hg_QWktTVyfr-0SQAC-QADVp29CpVlbqsqKxs2HwQ")

#Обработка кнопок с предметами
@dp.callback_query_handler(lambda c: c.data)
async def process_callback_buttons(callback_query: types.CallbackQuery):
    code = callback_query.data
    if (code == '0'):
        await bot.send_message(callback_query.from_user.id, get_subject("Русский язык"), reply_markup=MessageButtons)
    elif (code == '1'):
        await bot.send_message(callback_query.from_user.id, get_subject("Математика"), reply_markup=MessageButtons)
    elif (code == '2'):
        await bot.send_message(callback_query.from_user.id, get_subject("ИЗО"), reply_markup=MessageButtons)
    elif (code == '3'):
         await bot.send_message(callback_query.from_user.id, get_subject("Английский язык"), reply_markup=MessageButtons)
    elif (code == '4'):
        await bot.send_message(callback_query.from_user.id, get_subject("Всеобщая история"), reply_markup=MessageButtons)
    elif (code == '5'):
        await bot.send_message(callback_query.from_user.id, get_subject("История России"), reply_markup=MessageButtons)
    elif (code == '6'):
        await bot.send_message(callback_query.from_user.id, get_subject("Музыка"), reply_markup=MessageButtons)
    elif (code == '7'):
        await bot.send_message(callback_query.from_user.id, get_subject("Биология"), reply_markup=MessageButtons)
    elif (code == '8'):
        await bot.send_message(callback_query.from_user.id, get_subject("География"), reply_markup=MessageButtons)
    elif (code == '9'):
        await bot.send_message(callback_query.from_user.id, get_subject("Обществознание"), reply_markup=MessageButtons)
    elif (code == '10'):
        await bot.send_message(callback_query.from_user.id, get_subject("Технология"), reply_markup=MessageButtons)
    elif (code == '11'):
        await bot.send_message(callback_query.from_user.id, get_subject("Информатика"), reply_markup=MessageButtons)
    elif (code == '12'):
        await bot.send_message(callback_query.from_user.id, get_subject("Литература"), reply_markup=MessageButtons)
    elif (code == 'back'):
        await bot.send_message(callback_query.from_user.id, "Выбери нужный тебе предмет:", reply_markup=keyboard)
    elif (code == 'delete'):
        await callback_query.message.delete()
    await bot.answer_callback_query(callback_query.id)
#Парсер, отделяет нужное задание от всех остальных
def cut_subject(subject, post):
    date = ""
    for line in post.split('\n'):
        if "Всёдз за" in line or "#всёдз за" in line:
            date = line.replace("Всёдз", "Задание").replace("#всёдз", "Задание")
            break
    for name in subjects_names:
        post = post.replace(name, '$' + name)
    subjects = post.split('$')
    for i in subjects:
        if (subject in i):
            return date + '\n' + i

#Поиск нужного задания:
def get_subject(subject):
    sub = dbHandle.SelectFromKey(connection, subject)
    try:
        return cut_subject(subject, sub[-1][1])
    except:
        return "Ошибка: не удалось выполнить поиск!"

if __name__ == '__main__':
	executor.start_polling(dp)
