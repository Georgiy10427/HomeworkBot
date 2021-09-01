import config
import logging
import dbHandle
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
# Выше импорт необходимых модулей для работы бота

# задаем уровень логов
logging.basicConfig(level=logging.DEBUG)

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

SubscribeButtons = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Отписаться', callback_data='unsubscribe'),
    InlineKeyboardButton('Подписаться', callback_data='subscribe'))

OnlySubscribeButton = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Подписаться', callback_data='FirstSubscribe'))

CloseButton = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Закрыть', callback_data='delete'))

# Подключаемся к БД
connection = dbHandle.connect("database.db")
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
async def answer(message: types.Message):
    command = message.text
    search_request = ""
    if command.replace("/", "") in subjects_cmd:
        await bot.send_message(message.from_user.id,
                               get_subject(
                                   subjects_cmd[command.replace("/", "")]),
                               reply_markup=MessageButtons)
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


# Обработка кнопок
@dp.callback_query_handler(lambda c: c.data)
async def process_callback_buttons(callback_query: types.CallbackQuery):
    code = callback_query.data
    # Обработка школьных предметов:
    if str(code).isdigit():
        if 0 <= int(code) < len(subjects_names):
            await bot.send_message(callback_query.from_user.id,
                                   get_subject(subjects_names[int(code)]),
                                   reply_markup=MessageButtons)
        else:
            logging.error(f"The code {code} the ot of range.")
    # Возврат к меню
    elif code == 'back':
        await bot.send_message(callback_query.from_user.id, "Выбери нужный тебе предмет:", reply_markup=keyboard)
    # Удаление сообщения
    elif code == 'delete':
        await callback_query.message.delete()
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
    # Говорим телеграмму о том, что обработали нажатие кнопки:
    await bot.answer_callback_query(callback_query.id)


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


# Поиск нужного задания:
def get_subject(subject):
    sub = dbHandle.select_from_key(connection, subject)
    try:
        return cut_subject(subject, sub[-1][1])
    except Exception as e:
        logging.error(e)
        return "Ошибка: не удалось выполнить поиск!"


# Запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
