import requests
import logging
from bs4 import BeautifulSoup
import random

root_url = "https://gdz.ru"
subjects_urls = {
                "русский язык": "/russkii_yazik/baranova/%s-nom",
                "алгебра": "/algebra/nikolskiy-s-m/%s-nom",
                "английский язык": "/english/reshebnik-angliyskiy-v-fokuse-vaulina-yu-e/%s-s/",
                "география": "/geografiya/klimanova/%s-s/"
                }

geometry = {
    1: [1, 86],
    2: [87, 185],
    3: [186, 222],
    4: [223, 362],
    5: [363, 444],
    6: [445, 532],
    7: [533, 630],
    8: [631, 737],
    9: [738, 910],
    10: [911, 1010],
    11: [1011, 1077],
    12: [1078, 1147],
    13: [1148, 1183],
    14: [1184, 1310]
}


class Message(object):
    text = ""
    images = []


phrases = [
    "Взгляни, что я нашёл по предмету %s.",
    "Найдены ответы по предмету %s. Похоже, это то, что тебе нужно.",
    "Кажется это, что тебе нужно. Предмет - %s.",
    "Надеюсь, это то, что ты искал по предмету %s.",
    "Посмотри, это похоже на то, что тебе нужно по предмету %s.",
]


def get_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    img_content = soup.find_all('div', class_='with-overtask')
    m_images = []
    for image in img_content:
        images = image.find_all('img')
        for i in images:
            m_images.append(f'https:{i.attrs["src"]}')
    return m_images


def get_answer(subject_name: str, numbers: list, school_class: int):
    prepare_url = root_url
    link = ""
    if 1 <= school_class <= 11:
        prepare_url = f"{root_url}/class-{school_class}"
    else:
        logging.error(f"Некорректный класс: {school_class}")
        return -1

    messages = []
    for number in numbers:
        message = Message()
        if int(number) >= 3:
            if subject_name.lower() in subjects_urls:
                link = f"{prepare_url}{subjects_urls[subject_name.lower()] % number}"
                link = link.replace("\n", "")
            elif "геометрия" in subject_name.lower():
                for chapter in geometry:
                    if geometry[chapter][0] < int(number) < geometry[chapter][1]:
                        link = f"{prepare_url}/geometria/atanasyan-7-9/{chapter}-chapter-{number}/".replace("\n", "")
                        break
                else:
                    logging.error(f"Неправильно набран номер: {number}")
                    return -2
            else:
                logging.error(f"Неверный номер задания: {number}")
            print(link)
            message.images = get_content(link)
            message.text = \
                f"{random.choice(phrases) % f'{subject_name.lower()}, упражнение {number}'}".replace("\n", "")
            messages.append(message)
        else:
            logging.error(f"Некорректный номер задания: {number}")
    return messages
