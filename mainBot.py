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
Github (исходный код): https://github.com/Georgiy10427/HomeworkBot
"""
NotificationMSG = """
Если ты подпишешься на рассылку, то будешь получать уведомления о обновлениях заданий.
Ты в любой момент сможешь изменить свой выбор командой /notifications
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

#Создаём другие кнопки: закрыть, подписаться, вернуться в меню 
MessageButtons = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Вернуться в меню', callback_data='back'),
    InlineKeyboardButton('Закрыть', callback_data='delete'))

SubscribeButtons = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Отписаться', callback_data='unsubscribe'),
    InlineKeyboardButton('Подписаться', callback_data='subscribe'))

OnlySubscribeButton = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Подписаться', callback_data='FirstSubscribe'))

CloseButton = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Закрыть', callback_data='delete'))

#Подключаемся к БД (базе данных)
connection = dbHandle.Connect("database.db")
dbHandle.CreatePostsTable(connection)
dbHandle.CreateSubscribersTable(connection)

#Обработчик команды /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer_sticker("CAACAgIAAxkBAAEBO5VgiprjZ-LcWQABw12tF2wzdlqxoyIAAt4AA_R7GQABvYXvbvfFzj0fBA")
    await message.reply("Привет! Пожалуйста выбери нужный тебе предмет.", reply_markup=keyboard)
    await bot.send_message(message.from_user.id, NotificationMSG, reply_markup=OnlySubscribeButton)

#Обработчик команды /about
@dp.message_handler(commands=['about'])
async def process_about_command(message: types.Message):
    await message.reply(aboutMSG, reply_markup=CloseButton)

#Обработчик команды /notifications
@dp.message_handler(commands=['notifications'])
async def process_notifications_command(message: types.Message):
    await message.reply(NotificationMSG, reply_markup=SubscribeButtons)

#Обработчик других текстовых команд
@dp.message_handler()
async def answer(message: types.Message):
    command = message.text
    search_request = ""
    if message.from_user.id == config.owner_id and "/" in command:
        if "/add" in command:
            dbHandle.AddPost(connection, message.text.replace("/add ", ""))
            await message.reply("Добавлено!")
        elif "/edit" in command:
            parts = command.replace("/edit ", "").split(' && ')
            OldPost = dbHandle.SelectFromKey(connection, parts[0])[-1][-1]
            dbHandle.UpdateFromKey(connection, parts[0], parts[1])
            NewPost = dbHandle.SelectFromKey(connection, parts[1])[-1][-1]
            await message.reply("Отредактированно. До редактирования: \n" + OldPost +
            "\n" + "После: \n" + NewPost)
        elif "/notify" in command:
            subscribers = dbHandle.GetSubscribers(connection)
            notification = command.replace("/notify ", "")
            for user in subscribers:
                await bot.send_message(user[1], notification, reply_markup=CloseButton)
        elif "/delete" in command:
            post = dbHandle.SelectFromKey(connection, message.text.replace("/delete ", ""))
            dbHandle.DeleteFromKey(connection, message.text.replace("/delete ", ""))
            try:
                await message.reply("Удалено. Удалённый пост: \n" + post[-1][1])
            except:
                await message.reply("Возникла ошибка :( \nВозможно, данная публикация не существует ¯\\_(ツ)_/¯")
    else: #Можно удалить, т. к. использовать текстовые команды, которые нигде не объявлены пользователь вряд-ли будет использовать
        for subject in subjects_names:
            if subject in command:
                search_request = subject
                break
        if (search_request != ""): await message.reply(get_subject(search_request))
#        else:
#            await message.reply("Кажется, я не смогу тебе помочь")
#            await message.answer_sticker("CAACAgIAAxkBAAEBOzxgikgyP2ZGA-hg_QWktTVyfr-0SQAC-QADVp29CpVlbqsqKxs2HwQ")

#Обработка кнопок
@dp.callback_query_handler(lambda c: c.data)
async def process_callback_buttons(callback_query: types.CallbackQuery):
    code = callback_query.data
    #Обработка школьных предметов:
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
    elif (code == 'back'): #Возврат к меню
        await bot.send_message(callback_query.from_user.id, "Выбери нужный тебе предмет:", reply_markup=keyboard)
    elif (code == 'delete'): #Удаление сообщения
        await callback_query.message.delete()
    elif (code == 'subscribe'): #Подписываем пользователя к рассылке
        if(not dbHandle.IsSubscriber(connection, callback_query.from_user.id)):
            dbHandle.Subscribe(connection, callback_query.from_user.id)
            await bot.send_message(callback_query.from_user.id, "Хорошо, я тебя запомнил.", reply_markup=CloseButton)
        else:
            await bot.send_message(callback_query.from_user.id, "Ты уже подписан(а) на рассылку уведомлений. Где-то я тебя раньше видел...", reply_markup=CloseButton)
    elif (code == 'unsubscribe'): #Отписываем пользователя от рассылки
        if(dbHandle.IsSubscriber(connection, callback_query.from_user.id)):
            dbHandle.Unsubscribe(connection, callback_query.from_user.id)
            await bot.send_message(callback_query.from_user.id, "Теперь ты отписан(а) от рассылки.", reply_markup=CloseButton)
        else:
            await bot.send_message(callback_query.from_user.id, "Кажется, ты и так не подписан(а) на рассылку уведомлений.", reply_markup=CloseButton)
    elif (code == 'FirstSubscribe'): #Обработка предложения подписки на рассылку (при активации)
        if(not dbHandle.IsSubscriber(connection, callback_query.from_user.id)):
            dbHandle.Subscribe(connection, callback_query.from_user.id)
            await callback_query.message.edit_text("Вы успешно подписались на рассылку.")
            await callback_query.message.edit_reply_markup(CloseButton)
        else:
            await callback_query.message.edit_text("Ты уже был(а) подписан(а) на рассылку.")
            await callback_query.message.edit_reply_markup(CloseButton)
    await bot.answer_callback_query(callback_query.id) #Говорим телеграмму о том, что обработали нажатие кнопки

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

#Запускаем бота
if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)