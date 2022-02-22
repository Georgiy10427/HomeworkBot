import requests
import logging
from bs4 import BeautifulSoup
import numpy
import cv2


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


class Task(object):
    text = ""
    image = bytearray()
    url = ""
    number = 0
    img_width = 0
    img_height = 0
    current_variant = 0
    max_variant_value = 0


def get_image(url: str):
    try:
        response = requests.get(url, stream=True).raw
    except Exception as e:
        return e
    image_content = numpy.asarray(bytearray(response.read()), dtype=numpy.uint8)
    img = cv2.imdecode(image_content, -1)
    return img


def cv_to_bytes(img):
    return cv2.imencode('.jpg', img)[1].tobytes()


def get_content(url: str, var_number=1):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    variants = soup.find_all("figure")
    # Let's remove the video solutions and empty containers
    for j in variants:
        images = j.find_all("img")
        if not images:
            variants.pop(variants.index(j))
    for j in variants:
        text = str(j).lower()
        if "видеорешение" in text:
            variants.pop(variants.index(j))
    task_images = []
    images = variants[var_number-1].find_all("img")
    for i in images:
        task_images.append(f'https:{i.attrs["src"]}')
    return task_images


def get_max_variant_value(task: Task):
    response = requests.get(task.url)
    soup = BeautifulSoup(response.text, 'lxml')
    images = soup.find_all("figure")
    return len(images)


def get_tasks_urls(subject_name: str, numbers: list, school_class: int):
    prepare_url = root_url
    link = ""

    # Add school class to url
    if 1 <= school_class <= 11:
        prepare_url = f"{root_url}/class-{school_class}"
    else:
        logging.error(f"Некорректный класс: {school_class}")
        return -1

    tasks = []
    for number in numbers:
        task = Task()
        task.number = int(number)
        if int(number) >= 3:
            if subject_name.lower() in subjects_urls:
                link = f"{prepare_url}{subjects_urls[subject_name.lower()] % number}"
                link = link.replace("\n", "")
                task.url = link
                tasks.append(task)
            elif "геометрия" in subject_name.lower():
                for chapter in geometry:
                    if geometry[chapter][0] <= int(number) <= geometry[chapter][1]:
                        link = f"{prepare_url}/geometria/atanasyan-7-9/{chapter}-chapter-{number}/".replace("\n", "")
                        task.url = link
                        tasks.append(task)
                        break
                else:
                    logging.error(f"Неправильно набран номер: {number}")
                    continue
            else:
                logging.error(f"Неверный номер задания: {number}")
        else:
            logging.error(f"Некорректный номер задания: {number}")
    return tasks


def fold_images(images: list):
    return cv2.vconcat(images)


def get_answers(subject_name: str, numbers: list, school_class: int, var=1):
    tasks_urls: list = get_tasks_urls(subject_name, numbers, school_class)
    complete_tasks = []
    for task in tasks_urls:
        try:
            task_images_urls = get_content(task.url, var)
        except Exception as e:
            return e
        task_images = []
        for url in task_images_urls:
            task_images.append(get_image(url))
        task.image = fold_images(task_images)
        task.current_variant = var
        task.max_variant_value = get_max_variant_value(task)
        task.img_height, task.img_width = task.image.shape[:2]
        if "география" == subject_name.lower() or "английский язык" == subject_name.lower():
            task.text = f"{subject_name.lower().capitalize()}, страница {task.number}\n" \
                        f"Вариант {var} из {task.max_variant_value} вариантов"
        else:
            task.text = f"{subject_name.lower().capitalize()}, упражнение {task.number}\n" \
                        f"Вариант {var} из {task.max_variant_value} вариантов"
        complete_tasks.append(task)
    return complete_tasks
