from threading import Thread
from telebot import *
from os import environ as env
from pool import Pool
from replies import *
from database import Database
from user import User
from task import Task

bot = TeleBot(token=env["SIMPLE_POOL_TOKEN"])
db = Database()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, init_replies['start'])
    bot.register_next_step_handler(message, initialize)

def initialize(message):
    name = str(message.text)
    user = User(message.from_user.id, name)

    db.add_user(user)
    bot.send_message(message.chat.id, init_replies['finished'])

@bot.message_handler(commands=['push'])
def push(message):
    if message.from_user.id not in [int(u.id) for u in db.list_users()]:
        bot.reply_to(message, """Вы не авторизовались! Используйте команду /start, чтобы представиться системе""")
        return
    sent = bot.reply_to(message, task_creation_replies['get_name'])
    bot.register_next_step_handler(message, get_description, [sent])

def get_description(message, prev_data):
    user_id = message.from_user.id
    
    bot.edit_message_text(task_creation_replies['get_description'], prev_data[0].chat.id, prev_data[0].message_id)
    bot.register_next_step_handler(message, get_time, prev_data + [message.text])

def get_time(message, prev_data):
    user_id = message.from_user.id
    bot.edit_message_text(task_creation_replies['get_time'], prev_data[0].chat.id, prev_data[0].message_id)
    bot.register_next_step_handler(message, create_task, prev_data + [message.text])

def create_task(message, prev_data):
    prev_data += [message.text]
    if len(message.text) != 5 or (':' not in message.text): 
        bot.send_message(message.from_user.id, '❌  Неправильный формат времени')
    
    task = Task(prev_data[1], prev_data[2], prev_data[3], message.from_user.id, "DEFAULT")
    db.add_task(task)

    bot.send_message(message.chat.id, '✅  Задача записана')

def dispatch():
    while True:
        time.sleep(0.60)
        current_time = datetime.now().strftime("%H:%M")
        for user in db.list_users():
            for task in db.get_tasks(user.id):
                if task.time == current_time and task.state == 'DEFAULT': 
                    bot.send_message(user.id, f'🕔  Пора "{task.name}"!')
                    db.task_change_state(task, 'NOTIFIED_ONCE')

                if (datetime.strptime(task.time, '%H:%M') - datetime.strptime(current_time, '%H:%M')).total_seconds() > 9100 and task.state == "NOTIFIED_ONCE": 
                    bot.send_message(user.id, f'🕔  Пора "{task.name}"! x2')
                    db.task_change_state(task, 'NOTIFIED_TWICE')

                if (datetime.strptime(task.time, '%H:%M') - datetime.strptime(current_time, '%H:%M')).total_seconds() > 18200 and task.state == "NOTIFIED_TWICE": 
                    bot.send_message(user.id, f'🕔  Пора "{task.name}"! x3')
                    db.task_change_state(task, 'NOTIFIED_THREE_TIMES')



if __name__ == '__main__':
    print('⚡  Бот запущен')

    Thread(target=dispatch, daemon=True).start()
    bot.infinity_polling()