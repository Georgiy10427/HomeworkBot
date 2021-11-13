import aiogram.utils.exceptions
import config
import logging
import dbHandle
import sqlite3
import complete
import time
import cv2
from aiogram.types import *
from aiogram import Bot, Dispatcher, executor, types


logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

# Список всех предметов для парсера
subjects_names = ['Русский язык', 'Алгебра',
                  'ИЗО', "Литература",
                  'Английский язык', 'Всеобщая история',
                  'История России',
                  'Музыка', 'Физика', 'Биология',
                  'География', "Технология",
                  "Информатика", 'Обществознание', 'Геометрия']

subjects_cmd = {"russian": "Русский язык", "algebra": "Алгебра",
                "art": "ИЗО", "literature": "Литература",
                "english": "Английский язык",
                "history": "Всеобщая история",
                "russian_history": "История России",
                "music": "Музыка", "physics": "Физика",
                "bio": "Биология", "geography": "География",
                "technology": "Технология", "informatics": "Информатика",
                "social_studies": "Обществознание", "geometry": "Геометрия"}

timetable_cmd = "timetable"

aboutMSG = """
Бот призван помочь вам в поиске нужного домашнего задания. Сделан с акцентом на простоту и удобство)
Программа полностью свободна, с открытым исходным кодом.
Github (исходный код): https://github.com/Georgiy10427/HomeworkBot
"""
NotificationMSG = """
Если ты подпишешься на рассылку, то будешь получать уведомления о обновлениях заданий.
Ты в любой момент сможешь изменить свой выбор командой /notifications
"""

# Кнопки с названиями предметов
Russian = InlineKeyboardButton('Русский язык', callback_data='0')
Algebra = InlineKeyboardButton('Алгебра', callback_data='1')
Painting = InlineKeyboardButton('ИЗО', callback_data='2')
Literature = InlineKeyboardButton('Литература', callback_data='3')
English = InlineKeyboardButton('Английский язык', callback_data='4')
History = InlineKeyboardButton('Всеобщая история', callback_data='5')
RussianHistory = InlineKeyboardButton('История России', callback_data='6')
Music = InlineKeyboardButton('Музыка', callback_data='7')
Physics = InlineKeyboardButton('Физика', callback_data='8')
Bio = InlineKeyboardButton('Биология', callback_data='9')
Geography = InlineKeyboardButton('География', callback_data='10')
Technology = InlineKeyboardButton('Технология', callback_data='11')
ComputerScience = InlineKeyboardButton('Информатика', callback_data='12')
SocialScience = InlineKeyboardButton('Обществознание', callback_data='13')
Geometry = InlineKeyboardButton('Геометрия', callback_data='14')
Timetable = InlineKeyboardButton('Расписание', url=config.timetable_link)

# Создаём клавиатуру, добавляя в неё выше объявленные кнопки 
keyboard = InlineKeyboardMarkup(row_width=2) \
    .row(Russian, Algebra, Painting) \
    .row(Literature, English).row(History, RussianHistory) \
    .row(Music, Physics, Bio) \
    .row(Geography, Technology) \
    .row(ComputerScience, SocialScience) \
    .row(Geometry, Timetable)

# Создаём другие кнопки: закрыть, подписаться, вернуться в меню 
MessageButtons = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Меню', callback_data='back'),
    InlineKeyboardButton('Закрыть', callback_data='delete'))

MessageButtonsWithAnswer = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Меню', callback_data='back'),
    InlineKeyboardButton("Ответ", callback_data='answer'),
    InlineKeyboardButton('Закрыть', callback_data='delete'))

SubscribeButtons = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Отписаться', callback_data='unsubscribe'),
    InlineKeyboardButton('Подписаться', callback_data='subscribe'))

OnlySubscribeButton = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Подписаться', callback_data='FirstSubscribe'))

CloseButton = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Закрыть', callback_data='delete'))

AnswerButtons = InlineKeyboardMarkup().row(
    InlineKeyboardButton('Меню', callback_data='back'),
    InlineKeyboardButton('Закрыть', callback_data='delete')
)

ErrorButtons = InlineKeyboardMarkup().row(
    InlineKeyboardButton("Отправить отчёт", callback_data="forward_to_admin"),
    InlineKeyboardButton("Закрыть", callback_data="delete")
)


# Подключаемся к БД (базе данных)
connection = sqlite3.connect("database.sqlite")
dbHandle.create_posts(connection)
dbHandle.create_subscribers(connection)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer_sticker("CAACAgIAAxkBAAEBO5VgiprjZ-LcWQABw12tF2wzdlqxoyIAAt4AA_R7GQABvYXvbvfFzj0fBA")
    await message.reply("Привет! Пожалуйста выбери нужный тебе предмет.", reply_markup=keyboard)
    await bot.send_message(message.from_user.id, NotificationMSG, reply_markup=OnlySubscribeButton)


# Обработчик команды /about
@dp.message_handler(commands=['about'])
async def process_about_command(message: types.Message):
    await message.reply(aboutMSG, reply_markup=CloseButton)


# Обработчик команды /notifications
@dp.message_handler(commands=['notifications'])
async def process_notifications_command(message: types.Message):
    await message.reply(NotificationMSG, reply_markup=SubscribeButtons)


# Обработчик других текстовых команд
@dp.message_handler()
async def text_answer(message: types.Message):
    command = message.text
    search_request = ""
    if command.replace("/", "") in subjects_cmd:
        content = get_subject(subjects_cmd[command.replace("/", "")])
        if "|||" in content:
            await bot.send_message(message.from_user.id,
                                   content.split("|||")[0],
                                   reply_markup=MessageButtonsWithAnswer)
        else:
            await bot.send_message(message.from_user.id,
                                   content.split("|||")[0], reply_markup=MessageButtons)
    elif timetable_cmd in command.replace("/", ""):
        await bot.send_message(message.from_user.id,
                               "Ссылка на расписание",
                               reply_markup=InlineKeyboardMarkup()
                               .row(Timetable))
    elif message.from_user.id == config.owner_id and "/" in command:
        if "/add" in command:
            dbHandle.add_post(connection, message.text.replace("/add ", ""))
            await message.reply("Добавлено!")
        elif "/edit" in command:
            parts = command.replace("/edit ", "").split(' && ')
            old_post = dbHandle.select_from_key(connection, parts[0])[-1][-1]
            dbHandle.update_from_key(connection, parts[0], parts[1])
            new_post = dbHandle.select_from_key(connection, parts[1])[-1][-1]
            await message.reply(f"Отредактированно. До редактирования: \n {old_post} \n После: \n  {new_post}")
        elif "/notify" in command:
            subscribers = dbHandle.get_subscribers(connection)
            notification = command.replace("/notify ", "")
            for user in subscribers:
                await bot.send_message(user[1], notification, reply_markup=CloseButton)
        elif "/delete" in command:
            post = dbHandle.select_from_key(connection, message.text.replace("/delete ", ""))
            dbHandle.delete_from_key(connection, message.text.replace("/delete ", ""))
            try:
                await message.reply("Удалено. Удалённый пост: \n" + post[-1][1])
            except Exception as e:
                logging.error(e)
                await message.reply("Возникла ошибка :( \nВозможно, данная публикация не существует ¯\\_(ツ)_/¯")
    else:
        for subject in subjects_names:
            if subject in command:
                search_request = subject
                break
        if search_request != "":
            await message.reply(get_subject(search_request))


# Поиск нужного задания:
def get_subject(subject):
    sub = dbHandle.select_from_key(connection, subject)
    try:
        return cut_subject(subject, sub[-1][1])
    except Exception as e:
        logging.error(e)
        return "Ошибка: не удалось выполнить поиск!"


# Обработка кнопок
@dp.callback_query_handler(lambda c: c.data)
async def process_callback_buttons(callback_query: types.CallbackQuery):
    code = callback_query.data
    # Обработка школьных предметов:
    if str(code).isdigit():
        if 0 <= int(code) < len(subjects_names):
            content = get_subject(subjects_names[int(code)])
            if "|||" in content:
                await bot.send_message(callback_query.from_user.id,
                                       content.split("|||")[0],
                                       reply_markup=MessageButtonsWithAnswer)
            else:
                await bot.send_message(callback_query.from_user.id,
                                       content.split("|||")[0], reply_markup=MessageButtons)
        else:
            logging.error(f"The code {code} the out of range.")
    # Возврат к меню
    elif code == 'back':
        await bot.send_message(callback_query.from_user.id, "Выбери нужный тебе предмет:", reply_markup=keyboard)
    # Удаление сообщения
    elif code == 'delete':
        try:
            await callback_query.message.delete()
        except aiogram.utils.exceptions.MessageCantBeDeleted:
            await callback_query.answer("Невозможно удалить старое сообщение")
        except Exception as e:
            logging.error(e)
            await callback_query.answer("Произошла неизвестная ошибка")

    # Подписываем пользователя к рассылке
    elif code == 'subscribe':
        if not dbHandle.is_subscriber(connection, callback_query.from_user.id):
            dbHandle.subscribe(connection, callback_query.from_user.id)
            await bot.send_message(callback_query.from_user.id, "Хорошо, я тебя запомнил.", reply_markup=CloseButton)
        else:
            await bot.send_message(callback_query.from_user.id,
                                   "Ты уже подписан(а) на рассылку уведомлений. Где-то я тебя раньше видел...",
                                   reply_markup=CloseButton)
    # Отписываем пользователя от рассылки
    elif code == 'unsubscribe':
        if dbHandle.is_subscriber(connection, callback_query.from_user.id):
            dbHandle.unsubscribe(connection, callback_query.from_user.id)
            await bot.send_message(callback_query.from_user.id,
                                   "Теперь ты отписан(а) от рассылки.",
                                   reply_markup=CloseButton)
        else:
            await bot.send_message(callback_query.from_user.id,
                                   "Кажется, ты и так не подписан(а) на рассылку уведомлений.",
                                   reply_markup=CloseButton)
    # Обработка предложения подписки на рассылку (при активации)
    elif code == 'FirstSubscribe':
        if not dbHandle.is_subscriber(connection, callback_query.from_user.id):
            dbHandle.subscribe(connection, callback_query.from_user.id)
            await callback_query.message.edit_text("Вы успешно подписались на рассылку.")
            await callback_query.message.edit_reply_markup(CloseButton)
        else:
            await callback_query.message.edit_text("Ты уже был(а) подписан(а) на рассылку.")
            await callback_query.message.edit_reply_markup(CloseButton)
    # Поиск GDZ
    elif code == "answer":
        try:
            if "русский язык:" in callback_query.message.text.lower():
                await get_answer(callback_query, var=2)
            else:
                await get_answer(callback_query)
        except Exception as e:
            await bot.send_sticker(callback_query.from_user.id,
                                   "CAACAgUAAxkBAAEDOpZhhmHGlrx_q_QZoniqGX7HSXDypwACHAAD1UnhJlt52LObeelbIgQ")
            await bot.send_message(callback_query.from_user.id, f"Непредвиденная ошибка: {e}",
                                   reply_markup=ErrorButtons)
    # Пересылка отчёта админу
    elif code == "forward_to_admin":
        try:
            await callback_query.message.forward(config.owner_id)
            await callback_query.answer("Отчёт успешно отправлен.")
        except Exception as e:
            await bot.send_sticker(callback_query.from_user.id,
                                   "CAACAgUAAxkBAAEDOphhhmHRpuN8ho11CFk9bvnliCk7WAACIAAD1UnhJqrJn62Al-93IgQ")
            await bot.send_message(callback_query.from_user.id, f"Не удалось отправить отчёт, ошибка: {e}",
                                   reply_markup=CloseButton)
    await bot.answer_callback_query(callback_query.id)


async def get_answer(query: types.CallbackQuery, var=1):
    text_message: str = query.message.text
    current_subject: str = ""

    for subject in subjects_names:
        if subject in text_message:
            current_subject = subject
            break
    else:
        await query.answer("Ошибка: не удалось определить предмет.")
        return

    try:
        numbers: list = get_subject(current_subject) \
                            .split("|||")[1].replace(" ", "").replace("\n", "").split(",")
    except IndexError:
        await query.answer("Ошибка: не удалось определить номер задания.")
        return
    try:
        answers = complete.get_answers(current_subject, numbers, 7, var=var)
        if type(answers) != list:
            raise answers
    except Exception as e:
        await bot.send_sticker(query.from_user.id,
                               "CAACAgUAAxkBAAEDOpZhhmHGlrx_q_QZoniqGX7HSXDypwACHAAD1UnhJlt52LObeelbIgQ")
        await bot.send_message(query.from_user.id,
                               f"Ошибка сетевого соединения (сервер): {e}",
                               reply_markup=ErrorButtons)
        return
    for answer in answers:
        if answer.img_height > 840:
            filename = str(time.strftime('tmp/%Y%m%d-%H.%M.%S.jpg'))
            cv2.imwrite(filename, answer.image)
            file = InputFile(filename)
            await bot.send_document(query.from_user.id, document=file, caption=answer.text,
                                    reply_markup=AnswerButtons)
        else:
            await bot.send_photo(query.from_user.id, complete.cv_to_bytes(answer.image),
                                 answer.text, reply_markup=AnswerButtons)


async def next_answer(query: types.CallbackQuery):
    subject = query.message.caption.split("\n")[0].split(",")[0]
    text_message = query.message.caption.replace(" ", "").lower()
    text_message = text_message.replace("вариантов", "").replace("вариант", "")
    text_message = text_message.replace("упражнение", "").replace("страница", "")
    number = text_message.split("\n")[0].split(",")[1].replace("\n", "")
    variant = text_message.split("\n")[1].split("из")[0]
    max_variant_value = text_message.split("\n")[1].split("из")[1]
    print(number)
    if variant == int(max_variant_value):
        variant = 1
    else:
        variant = int(variant) + 1
    answers = complete.get_answers(subject, [int(number)], 7, var=variant)
    task_answer = answers[0]
    cv2.imwrite("img.jpg", task_answer.image)
    await query.message.edit_caption(task_answer.text, reply_markup=AnswerButtons)
    await query.message.edit_media(complete.cv_to_bytes(task_answer.image))


# Парсер, отделяет нужное задание от всех остальных
def cut_subject(subject, post):
    date = ""
    for line in post.split('\n'):
        if "Всёдз за" in line or "#всёдз за" in line:
            date = line.replace("Всёдз", "Задание").replace("#всёдз", "Задание")
            break
    for name in subjects_names:
        post = post.replace(name, f'${name}')
    subjects = post.split('$')
    for i in subjects:
        if subject in i:
            return date + '\n' + i


# Запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
