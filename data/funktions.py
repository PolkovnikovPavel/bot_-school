import random, vk_api
from vk_api.keyboard import VkKeyboard


def init(v):
    global vk
    vk = v


def say(man, text, response):
    try:
        string = '___________________\n'
        string += f'  | сообщение от {response[0]["first_name"]} {response[0]["last_name"]}\n\|/\n'

        string += text + '\n/|\ \n  | конец\n___________________'
        write_msg(man, string)
    except:
        return False
    return True


def write_msg(user_id, message, attachment='', keyboard=None):
    vk.messages.send(user_id=user_id,
                     message=message,
                     random_id=random.randint(0, 2 ** 64),
                     attachment=attachment,
                     keyboard=create_keyboard())


def create_keyboard():
    keyboard = vk_api.keyboard.VkKeyboard(one_time=False)
    keyboard.add_button("ответы")
    keyboard.add_button("добавить ответ")
    keyboard.add_line()
    keyboard.add_button("help")
    keyboard.add_button("рандом!")
    keyboard.add_line()
    keyboard.add_button("расписание на сегодня")

    return keyboard.get_keyboard()
