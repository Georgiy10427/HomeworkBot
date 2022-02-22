import aiogram.utils.exceptions
import config
import logging
import dbHandle
import complete
import time
import cv2
import asyncio
import random
from aiogram.types import *
from aiogram import Bot, Dispatcher, executor, types, filters
import stickers
import threading
import concurrent.futures

version = 1.33

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

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


keyboard = InlineKeyboardMarkup(row_width=2) \
    .row(Russian, Algebra, Painting) \
    .row(Literature, English).row(History, RussianHistory) \
    .row(Music, Physics, Bio) \
    .row(Geography, Technology) \
    .row(ComputerScience, SocialScience) \
    .row(Geometry, Timetable) \


MessageButtons = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Меню', callback_data='menu'),
    InlineKeyboardButton('Назад', callback_data='back'),
    InlineKeyboardButton('Закрыть', callback_data='delete'))

MessageButtonsWithAnswer = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Меню', callback_data='menu'),
    InlineKeyboardButton('Назад', callback_data='back'),
    InlineKeyboardButton("Ответ", callback_data='answer'),
    InlineKeyboardButton('Закрыть', callback_data='delete'))

SubscribeButtons = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Отписаться', callback_data='unsubscribe'),
    InlineKeyboardButton('Закрыть', callback_data='delete'),
    InlineKeyboardButton('Подписаться', callback_data='subscribe'))

OnlySubscribeButton = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Подписаться', callback_data='first_subscribe'))

CloseButton = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Закрыть', callback_data='delete'))

AnswerButtons = InlineKeyboardMarkup().row(
    InlineKeyboardButton('Меню', callback_data='menu'),
    InlineKeyboardButton('Закрыть', callback_data='delete')
)

ErrorButtons = InlineKeyboardMarkup().row(
    InlineKeyboardButton("Отправить отчёт", callback_data="forward_to_admin"),
    InlineKeyboardButton("Закрыть", callback_data="delete")
)


#asyncio.run(dbHandle.create_posts(dbHandle.get_url()))
#asyncio.run(dbHandle.create_subscribers(dbHandle.get_url()))


@dp.message_handler(filters.Command('start', ignore_case=True))
async def process_start_command(message: types.Message):
    await message.answer_sticker(random.choice(stickers.hi))
    if not await dbHandle.is_subscriber(dbHandle.get_url(), message.from_user.id):
        await bot.send_message(message.from_user.id,
                               "Привет! Пожалуйста выбери нужный тебе предмет.",
                               reply_markup=keyboard)
        await bot.send_message(message.from_user.id, NotificationMSG, reply_markup=OnlySubscribeButton)
    else:
        await bot.send_message(message.from_user.id,
                               "Выбери нужный тебе предмет:",
                               reply_markup=keyboard)
    await message.delete()


@dp.message_handler(filters.Command('about', ignore_case=True))
async def process_about_command(message: types.Message):
    await bot.send_message(message.from_user.id, aboutMSG, reply_markup=CloseButton)
    await message.delete()


@dp.message_handler(filters.Command('notifications', ignore_case=True))
async def process_notifications_command(message: types.Message):
    await bot.send_message(message.from_user.id, NotificationMSG, reply_markup=SubscribeButtons)
    await message.delete()


@dp.message_handler(filters.Command('clear_history_notification'))
async def clear_history_notification(message: types.Message):
    if message.from_user.id != config.owner_id:
        return None
    subscribers = await dbHandle.get_subscribers(dbHandle.get_url())
    notification = "Мы обновили чат бота. Пожалуйста очистите историю чата во избежании ошибок"
    for user in subscribers:
        await asyncio.sleep(0.2)
        try:
            await bot.send_sticker(user[1], stickers.update)
            await bot.send_message(user[1], notification, reply_markup=CloseButton)
        except Exception as e:
            logging.error(f"{e}: {user[1]}")
            continue


@dp.message_handler(filters.Command('notify'))
async def send_notification(message: types.Message):
    if message.from_user.id != config.owner_id:
        return None
    subscribers = await dbHandle.get_subscribers(dbHandle.get_url())
    notification = message.text.replace("/notify ", "")
    notification = notification.replace("/notify", "")
    if notification == "":
        return None
    for user in subscribers:
        await asyncio.sleep(0.2)
        try:
            await bot.send_message(user[1], notification, reply_markup=CloseButton)
        except Exception as e:
            logging.error(f"{e}: {user[1]}")
            continue


@dp.message_handler()
async def text_answer(message: types.Message):
    command = message.text.replace("/", "")
    if command in subjects_cmd:
        subject = subjects_cmd[command]
        content = await dbHandle.select_from_key(dbHandle.get_url(), subject)
        content = content[-1]
        has_answer = "|||" in cut_subject(subject, content[1])
        reply_markup = make_task_buttons(has_answer, content[0])
        text = cut_subject(subject, content[1])
        if has_answer:
            text = cut_subject(subject, content[1]).split("|||")[0]
        await bot.send_message(message.from_user.id,
                               text,
                               reply_markup=reply_markup)
    elif timetable_cmd in command:
        await bot.send_message(message.from_user.id,
                               "Ссылка на расписание",
                               reply_markup=InlineKeyboardMarkup()
                               .row(Timetable))
    elif message.from_user.id == config.owner_id:
        if "add" in command:
            await dbHandle.add_post(dbHandle.get_url(), message.text.replace("/add ", ""))
            await message.reply("Добавлено!")
    if command == "clear_history_notification" \
       or command == "notify":
        return
    await message.delete()


async def get_subject(subject):
    sub = await dbHandle.select_from_key(dbHandle.get_url(), subject)
    try:
        return cut_subject(subject, sub[-1])
    except Exception as e:
        logging.error(e)
        return "Ошибка: не удалось выполнить поиск!"


def make_task_buttons(has_answer: bool, task_id: int):
    menu_key = InlineKeyboardButton("Меню", callback_data="menu")
    back_key = InlineKeyboardButton("Назад", callback_data=f"back={task_id}")
    answer_key = InlineKeyboardButton("Ответ", callback_data="answer")
    close_key = InlineKeyboardButton("Закрыть", callback_data="delete")
    if has_answer:
        return InlineKeyboardMarkup() \
            .row(menu_key, back_key, answer_key, close_key)
    else:
        return InlineKeyboardMarkup() \
            .row(menu_key, back_key, close_key)


@dp.callback_query_handler(lambda c: str(c.data).isdigit())
async def get_tasks(query: types.CallbackQuery):
    subject = subjects_names[int(query.data)]
    content = await dbHandle.select_from_key(dbHandle.get_url(), subject)
    content = content[-1]
    has_answer = "|||" in cut_subject(subject, content[-1])
    reply_markup = make_task_buttons(has_answer, content[0])
    text = cut_subject(subject, content[-1])
    if has_answer:
        text = text.split("|||")[0]
    text = text.replace("#всёдз", "Задание")
    await bot.send_message(query.from_user.id,
                           text,
                           reply_markup=reply_markup)
    await bot.answer_callback_query(query.id)


@dp.callback_query_handler(lambda c: c.data == "menu")
async def get_menu(query: types.CallbackQuery):
    await bot.send_message(query.from_user.id,
                           "Выбери нужный тебе предмет:",
                           reply_markup=keyboard)
    await bot.answer_callback_query(query.id)


@dp.callback_query_handler(lambda c: c.data == "delete")
async def delete_message(query: types.CallbackQuery):
    try:
        await query.message.delete()
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        await query.answer("Невозможно удалить старое сообщение")
    except Exception as e:
        logging.error(e)
        await query.answer("Произошла неизвестная ошибка")
    await bot.answer_callback_query(query.id)


@dp.callback_query_handler(lambda c: c.data == "subscribe")
async def subscribe_user(query: types.CallbackQuery):
    if not await dbHandle.is_subscriber(dbHandle.get_url(), query.from_user.id):
        await dbHandle.subscribe(dbHandle.get_url(), query.from_user.id)
        await bot.send_message(query.from_user.id, "Хорошо, я тебя запомнил.", reply_markup=CloseButton)
    else:
        await bot.send_message(query.from_user.id,
                               "Ты уже подписан(а) на рассылку уведомлений. Где-то я тебя раньше видел...",
                               reply_markup=CloseButton)
    await bot.answer_callback_query(query.id)


@dp.callback_query_handler(lambda c: c.data == "unsubscribe")
async def unsubscribe_user(query: types.CallbackQuery):
    if dbHandle.is_subscriber(dbHandle.get_url(), query.from_user.id):
        await dbHandle.unsubscribe(dbHandle.get_url(), query.from_user.id)
        await bot.send_message(query.from_user.id,
                               "Теперь ты отписан(а) от рассылки.",
                               reply_markup=CloseButton)
    else:
        await bot.send_message(query.from_user.id,
                               "Кажется, ты и так не подписан(а) на рассылку уведомлений.",
                               reply_markup=CloseButton)
    await bot.answer_callback_query(query.id)


@dp.callback_query_handler(lambda c: c.data == "first_subscribe")
async def first_subscribe(query: types.CallbackQuery):
    if not await dbHandle.is_subscriber(dbHandle.get_url(), query.from_user.id):
        await dbHandle.subscribe(dbHandle.get_url(), query.from_user.id)
        await query.message.edit_text("Вы успешно подписались на рассылку.")
        await query.message.edit_reply_markup(CloseButton)
    else:
        await query.message.edit_text("Ты уже был(а) подписан(а) на рассылку.")
        await query.message.edit_reply_markup(CloseButton)
    await bot.answer_callback_query(query.id)


@dp.callback_query_handler(lambda c: c.data == "answer")
async def send_answer(query: types.CallbackQuery):
    try:
        if "русский язык:" in query.message.text.lower():
            await get_answer(query, var=2)
        else:
            await get_answer(query)
    except Exception as e:
        await bot.send_sticker(query.from_user.id, stickers.answer_error)
        await bot.send_message(query.from_user.id, f"Непредвиденная ошибка: {e}",
                               reply_markup=ErrorButtons)
        logging.error(e)
    await bot.answer_callback_query(query.id)


@dp.callback_query_handler(lambda c: c.data == "forward_to_admin")
async def forward_report(query: types.CallbackQuery):
    try:
        await query.message.forward(int(config.owner_id))
        await query.answer("Отчёт успешно отправлен.")
    except Exception as e:
        await bot.send_sticker(query.from_user.id, stickers.error_report)
        await bot.send_message(query.from_user.id, f"Не удалось отправить отчёт, ошибка: {e}",
                               reply_markup=CloseButton)
        logging.error(e)
    await bot.answer_callback_query(query.id)


back_cmd = \
    lambda c: \
    str(c.data).split("=")[0] == "back" \
    and str(c.data).split("=")[1].isdigit()


@dp.callback_query_handler(back_cmd)
async def get_prev_task(query: types.CallbackQuery):
    await get_prev_note(query, query.message)
    await bot.answer_callback_query(query.id)


async def get_prev_note(query, message: types.Message):
    try:
        current_id = int(query.data.split("=")[1])
    except Exception as e:
        logging.error(e)
        await query.answer("Неверный запрос")
    try:
        text_message: str = message.text.split("\n")[1]
        subject = text_message.split(":")[0]
    except Exception as e:
        logging.error(e)
        await query.answer("Девиантная публикация")
        return None

    try:
        prev_note = await dbHandle.get_task_where_id_less(dbHandle.get_url(), current_id, subject)
        prev_note = prev_note[-1]
        prev_note_id = prev_note[0]
        prev_note = prev_note[-1]
    except IndexError:
        prev_note = await dbHandle.select_from_key(dbHandle.get_url(), subject)
        prev_note = prev_note[-1]
        prev_note_id = prev_note[0]
        has_answer = "|||" in prev_note[1]
        reply_markup = make_task_buttons(has_answer, prev_note_id)
        if has_answer:
            prev_note = prev_note[-1].split("|||")[0]
        await message.edit_text(cut_subject(subject, prev_note))
        await message.edit_reply_markup(reply_markup)
        await query.answer("Вы пролистали все задания")
        return None
    has_answer = False
    try:
        note = cut_subject(subject, prev_note)
        has_answer = "|||" in note
        reply_markup = make_task_buttons(has_answer, prev_note_id)
        prev_note = note
        if has_answer:
            prev_note = note.split("|||")[0]
    except Exception as e:
        logging.error(e)
        prev_note = f"Ошибка поиска: {e}"
    await message.edit_text(prev_note)
    await message.edit_reply_markup(reply_markup)


async def get_src_task(message: types.Message):
    task = message.text.split("\n")[1]
    subject = task.split(":")[0]
    src_note = await dbHandle.select_from_key(dbHandle.get_url(), task)
    src_note = src_note[-1][-1]
    return cut_subject(subject, src_note)


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
        numbers = await get_src_task(query.message)
        numbers = numbers.split("|||")[1].replace(" ", "").replace("\n", "").split(",")
    except IndexError:
        await query.answer("Ошибка: не удалось определить номер задания.")
        return
    try:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ProcessPoolExecutor() as pool:
            answers = await loop.run_in_executor(
                pool, complete.get_answers,
                current_subject, numbers, 7, var
            )
        if type(answers) != list:
            raise answers
    except Exception as e:
        await bot.send_sticker(query.from_user.id, stickers.answer_error)
        await bot.send_message(query.from_user.id,
                               f"Ошибка сетевого соединения (сервер): {e}",
                               reply_markup=ErrorButtons)
        return
    for answer in answers:
        if answer.img_height > 840:
            filename = time.strftime('tmp/%Y%m%d-%H.%M.%S.jpg')
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
