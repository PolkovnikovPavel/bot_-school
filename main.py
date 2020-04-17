import datetime
import wikipedia, requests, json

from vk_api.longpoll import VkLongPoll, VkEventType
from data import db_session
from data.funktions import *
from data.answers import Answers

import key_words


db_session.global_init("db/answers.sqlite")
week = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница',  'суббота', 'воскресенье']
wikipedia.set_lang('ru')

# API-ключ созданный ранее
token = "fcc9af59ec1fc88e6397f47251edff1dcae479b8244be6c762d30e01ecb8a60ad90256eb5b79d39e28c54"
login, password = '89505876657', ''
users = {}

# Авторизуемся как сообщество
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
init(vk)

vk_session_man = vk_api.VkApi(login, password)
vk_session_man.auth(token_only=True)

# Работа с сообщениями
longpoll = VkLongPoll(vk_session)

print("Server started")
for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            vk = vk_session.get_api()
            response = vk.users.get(user_id=event.user_id)

            print(event)
            print('Новое сообщение:')
            print('Для меня от:', response)
            print('Текст:', event.text)

            attachment = ''
            str = f'Я не понимаю вас, а чтоб понимал воспользуйтесь командами. Чтоб узнать команды напиши "что ты можешь?" или "help"'

            if event.text.lower() == 'как дела' or event.text.lower() == 'чё как':
                str = 'Круто, мне массаж делают, чтоб я мог больше, а у тебя?'

            elif event.text.lower() == 'описание':
                str = key_words.description_text

            elif event.text.lower() == 'привет' or event.text.lower() == 'хай':
                str = 'Привет привет'

            elif any(map(lambda x: event.text.lower() == x, key_words.help)):
                str = key_words.text_help

            elif any(map(lambda x: x in event.text.lower(), key_words.time)):
                moscow_time = datetime.datetime.now()
                date = f'{moscow_time.year}-{moscow_time.month}-{moscow_time.day}'
                time = f'{moscow_time.hour}:{moscow_time.minute}:{moscow_time.second}'
                weekday = week[moscow_time.weekday()]

                str = f"дата: {date}\nвремя: {time}\nдень недели: {weekday}"

            elif 'что такое ' in event.text.lower():
                try:
                    request = event.text.lower().split('что такое ')[-1]
                    str = wikipedia.summary(request, sentences=3)
                    str += f'\nДля более подробной информации {wikipedia.page(request).url}'
                except:
                    str = 'Увы, но по вашему запросу не удалось ничего найти'

            elif 'скажи админу ' in event.text.lower():
                str = 'Сообщение успешно отправлено!'
                request = event.text.lower().split('скажи админу ')[-1]
                if not say(449876815, request, response):
                    str = 'Ошибка в отправке'

            elif 'скажи субадмину ' in event.text.lower():
                str = 'Сообщение успешно отправлено!'
                request = event.text.lower().split('скажи субадмину ')[-1]
                if not say(264941371, request, response):
                    str = 'Ошибка в отправке'

            elif any(map(lambda x: event.text.lower() == x, key_words.random)):
                answer = requests.get(
                    'https://api.thecatapi.com/v1/images/search').text
                img = json.loads(answer)
                str = f"Случайный котик! {img[0]['url']}"

            elif 'расписание на' == ' '.join(event.text.lower().split()[:2]):
                day = event.text.lower().split()[2]
                weekdays = {'пн': 0, 'вт': 1, 'ср': 2, 'чт': 3, 'пт': 4, 'сб': 5, 'вс': 6,
                            'понедельник': 0, 'вторник': 1, 'среду': 2, 'четверг': 3,
                            'пятницу': 4, 'субботу': 5, 'воскресенье': 6}
                if day == 'сегодня':
                    time = datetime.datetime.now()
                    day = time.weekday()
                else:
                    try:
                        day = weekdays[day]
                    except:
                        day = 99
                if day == 99:
                    str = 'Не удалось найти такой день недели :('
                else:
                    str = key_words.timetable[day]


            elif 'ответы' == event.text.lower():
                session = db_session.create_session()
                answers = session.query(Answers).all()
                str = ['Вот все имеющиеся задания:']
                for i in range(len(answers)):
                    answer = answers[i]
                    str.append(f'{i + 1}: {answer.description}')
                str = '\n'.join(str)
                if len(answers) == 0:
                    str = 'В базе пока нет ответов, но вы можете их добавить, написав "добавить ответ"!'
            elif 'добавить ответ' == event.text.lower():
                users[event.user_id] = [1]
                str = 'Введите подробно название задания'

            elif event.user_id in users and users[event.user_id][0] == 1:
                users[event.user_id].append(event.text + ' - ' + response[0]["last_name"])
                users[event.user_id][0] = 2
                str = 'Введите очень подробно ответ, желательно указать какую оценку горантирует этот ответ и дату, чтоб было понятней. К сожеленью пока фото не возможно прикреплять'

            elif event.user_id in users and users[event.user_id][0] == 2:
                session = db_session.create_session()
                users[event.user_id].append(event.text)
                users[event.user_id][0] = 0

                answer = Answers(
                    description=users[event.user_id][1],
                    text=users[event.user_id][2],
                    photo = event.attachments
                )
                session.add(answer)
                session.commit()

                str = 'спасибо за ваш ответ, он кому-нибудь поможет'

            elif 'удали' == event.text.lower().split()[0]:
                if any(map(lambda x: x == event.user_id, key_words.id_of_vip)):
                    nums = event.text.lower().split()[1:]
                    session = db_session.create_session()
                    answers = session.query(Answers).all()
                    for num in nums:
                        try:
                            answer = answers[int(num) - 1]
                            session.delete(answer)
                        except:
                            pass
                    session.commit()
                    str = f'Были успешно удалены номера: {", ".join(nums)}'
                else:
                    str = 'У вас нет прав на эту комманду'

            elif event.text.isdigit():
                session = db_session.create_session()
                answers = session.query(Answers).all()
                num = int(event.text)

                if num > len(answers):
                    str = 'Такого номера ответа нет'
                else:
                    photos = answers[num - 1].photo

                    """
                    attach = []
                    for i in range(len(photos) // 2):
                        type, name = photos[f'attach{i + 1}_type'], photos[f'attach{i + 1}']
                        attach.append(type+name)
                    ' '.join(attach)
                    attachment = attach[0]
                    """

                    str = f'Ответ на задание №{num}:\n\n{answers[num - 1].text}\n_______________\nконец ответа.'
            elif 'synchronization_12321' == event.text.lower():
                session = db_session.create_session()
                answers = session.query(Answers).all()
                str = '\n'.join(list(map(lambda x: f'{x.id}<//>{x.description}<//>{x.text}<//>{x.photo}', answers)))

            write_msg(event.user_id, str, attachment)

