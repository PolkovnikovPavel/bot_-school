import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


def write_msg(user_id, message, attachment=''):
    vk.messages.send(user_id=user_id,
                     message=message,
                     random_id=random.randint(0, 2 ** 64),
                     attachment=attachment)


# API-ключ созданный ранее 
token = "fcc9af59ec1fc88e6397f47251edff1dcae479b8244be6c762d30e01ecb8a60ad90256eb5b79d39e28c54"
login, password = '89505876657', ''

vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
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

            elif event.text.lower() == 'привет' or event.text.lower() == 'хай':
                str = 'Привет привет'
            elif not response[0]["first_name"] == 'саня' and response[0]["last_name"] == 'елесеев':
                str = 'ты лох'


            write_msg(event.user_id, str, attachment)
