# HomeworkBot
Чат-бот позволяет узнать текущие домашнее задание по нужному предмету, всего в пару кликов. 

![Image alt](https://github.com/Georgiy10427/HomeworkBot/blob/main/screenshot.png)

# Попробовать бота
Вы можете протестировать работу данного кода на примере бота @AllHomework_bot в телеграмме. 
# Установка

## 1. Создаём бота в Telegram

Бот в Telegram создается при помощи другого бота под названием BotFather. Отправляем ему команду /newbot, выбираем имя, которое будет отображаться в списке контактов, и адрес. Например, «Тестовый бот» с адресом «test123_bot».

Если адрес не занят, а имя введено правильно, BotFather пришлет в ответ сообщение с токеном — «ключом» для доступа к созданному боту. Его нужно сохранить и никому не показывать.

## 2. Установка зависимостей
На компьютере должен быть установлен минимум Python 3.8 или выше. Если вы сами собираете Python, то он должен быть собран [с поддержкой sqlite](https://stackoverflow.com/questions/1210664/no-module-named-sqlite3). 
Установите библиотеку aiogram:

**Windows**:
```
pip install aiogram
```
**GNU/Linux** или **Mac OS**:
```
pip3 install aiogram
```
**GNU/Linux** (самособранный Python или при наличии нескольких его версий):
```
pip3.8 install aiogram
```
## 3. Запуск
#### 3.1 Загрузка кодов бота
Скачайте [исходные коды](https://github.com/Georgiy10427/HomeworkBot/archive/refs/heads/main.zip) бота в виде архива и распакуйте его куда-нибудь. 
Или используйте git (если он установлен): 

``` git clone https://github.com/Georgiy10427/HomeworkBot.git ``` 
#### 3.2 Настройка бота 
В папке с исходными кодами найдите файл config.py и подставьте туда свой API Token, ранее полученный в шаге 1. В итоге значение API_TOKEN в файле config.py должно выглядеть примерно так:
> API_TOKEN = 'ВАШ_ТОКЕН' #Токен бота из @BotFather

Вместо ВАШ_ТОКЕН должен быть подставлен токен из бота @BotFather (шаг 1). 
Однако вы не сможете добавлять, редактировать задания или создавать рассылки, т. к. бот не знает ID владельца. Чтобы узнать свой ID вы можете воспользоваться ботом @userinfobot 

Подставьте полученный ID вместо 0 в этом же файле (config.py). 
> owner_id = 0
#### 3.3 Запуск бота 
Для запуска бота, как обычной программы перейдите в директорию с исходными кодами и используйте команду:

**Windows**:
```python MainBot.py```

**GNU/Linux**:
```python3 MainBot.py```

**GNU/Linux** (самособранный Python или при наличии нескольких его версий):
``` python3.8 MainBot.py ```
## 4. Запуск бота на сервере
#### 4.1 Подключитесь к серверу по протоколлу SSH.
Для этого на GNU/Linux или Mac OS вы можете использовать стандартную утилиту для ssh, вызвав её командой: 
```
ssh ИМЯ_ПОЛЬЗОВАТЕЛЯ@IP_АДРЕС_СЕРВЕРА
``` 
Если вы используете Windows вы можете попробовать программу [PuTTY](https://www.putty.org/) 
#### 4.2 Установка менеджера процессов 
Нам нужно установить удобный менеджер процессов PM2 и язык программирования NodeJS с менеджером пакетов npm для его работы:

Серверная OS - Debian (10 и выше)/Ubuntu и им подобные:
```
sudo apt install nodejs
sudo apt install npm
npm install pm2 -g
```
#### 4.3 Загрузка бота на сервер
Загрузите исходные коды бота на сервер, например с помощью [FileZilla](https://filezilla-project.org/) или панели вашего хостинга. 
#### 4.4 Запуск 
Перейдите в директорию, в которую вы ранее загрузили файлы бота и выполните в ней команду:
```
pm2 start mainBot.py --interpreter=python3
```

или, если на сервере несколько версий Python:

```
pm2 start mainBot.py --interpreter=python3.8
```
Бот запущен. Чтобы просмотреть его состояние выполните команду:
```
pm2 list
```

Чтобы завершить работу бота используйте:

```
pm2 kill
```

## 5. Управление ботом
#### Добавляем задания
Чтобы добавить задания отправьте в диалоге с ботом команду ```/add ```:
Например, так:
```
/add #всёдз за 23 февраля
Математика: №467
Биология: параграф 41, читать
Литература: читать 12 подвигов Геракла 
``` 
Бот в ответ напишет:
> Добавленно!

Разберём данный пример. Для указания даты используется тэг ```#всёдз``` или ```Всёдз``` (вы можете изменить эти теги в коде ```main.py```), бот при выдаче заданий меняет эти тэги на ```Задание```. Дальше идут названия предметов с заданиями, названия можно задать в списке ```subjects_names``` в ковычках, через запятую. Бот заранее зная названия всех предметов может автоматически поделить ваш пост на задания. Обязательно следует соблюдать синтаксис для корректной обработки:
```
/add #всёдз за 23 февраля
Предмет1: какое-либо задание 
Предмет2: какое-либо задание 
Предмет3: какое-либо задание 
``` 
Нумерация предметов как не странно не нужна. 

#### Редактируем задания
Редактирования поста выполняется командой ```/edit``` После команды пишется ключевая фраза для поиска, затем сочетание ``` && ``` для разделения, в конце пишется отредактированный вами пост.
Например:
```
/edit #всёдз за 23 февраля && #всёдз за 23 февраля
Математика: №468
Биология: параграф 41, читать
Литература: читать 13-й подвиг Геракла
```
Бот найдёт пост по указанному ключу для поиска/фразе и отредактирует его так, как вы указали после знака ```&&```. В ответном сообщении бот вернёт вам пост до редактирования и после. Например:
>Отредактированно. До редактирования:  
>#всёдз за 30 апреля  
>Математика: №467  
>Биология: параграф 41, читать  
>Литература: читать 12 подвигов Геракла  
>После:  
>#всёдз за 23 февраля && #всёдз за 23 февраля  
>Математика: №468  
>Биология: параграф 41, читать  
>Литература: читать 13-й подвиг Геракла  

#### Удаляем задания
Тут всё просто: ```/delete #всёдз за 23 февраля```
Команда ```/delete``` говорит боту о том, что надо найти и удалить такой-то пост. Следом за командой вводится ключевая фраза для поиска и удаления. В ответ бот сообщит об удалении и прекрепит пост, который он удалил. Пример:
>Удаленно. Удалённый пост:  
>#всёдз за 23 февраля  
>Математика: №467  
>Биология: параграф 41, читать  
>Литература: читать 12 подвигов Геракла  

# Лицензия
Программа с открытым кодом, распространяется под свободной лицензией GNU GPL 3. 
