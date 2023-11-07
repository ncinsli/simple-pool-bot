from sqlite3 import *
from task import Task
from user import User

class Database:
    def __init__(self):
        self.connection = connect('./database.db', check_same_thread=False)
        self.cursor = self.connection.cursor()

    def reset(self):
        try:
            self.exec('DROP TABLE Users')
            self.exec('DROP TABLE Tasks')
        except: pass
        self.exec('''CREATE TABLE Users(
            Id TEXT,
            Name TEXT
        )''')

        self.exec('''CREATE TABLE Tasks(
            Name TEXT,
            Description TEXT,
            Time TEXT,
            User_Id TEXT,
            State TEXT
        )''')
    
    def add_user(self, user: User):
        self.exec(f"""INSERT INTO Users VALUES("{user.id}", "{user.name}")
        """)

    def remove_user(self, user: User):
        self.exec(f'''DELETE FROM Users WHERE Id="{user.id}" AND Name="{user.name}"''')

    def list_users(self):
        raw = self.exec_get('''SELECT * FROM Users''')
        return [User(id, name) for id, name in raw]
    
    def add_task(self, task: Task):
        self.exec(f"""INSERT INTO Tasks VALUES("{task.name}", "{task.description}", "{str(task.time)}", "{task.user_id}", "{task.state}")
        """)
    
    def remove_task(self, task: Task):
        self.exec(f"""DELETE FROM Tasks WHERE Name="{task.name}" AND  Description="{task.description}" AND Time="{str(task.time)}" AND User_Id="{task.user_id}"
        """)
    
    def exec(self, query):
        self.cursor.execute(query)
        self.connection.commit()

    def exec_get(self, query):
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.connection.commit()
        return result
    
    def get_tasks(self, user_id: str):
        raw = self.exec_get(f'''SELECT * FROM Tasks WHERE User_Id="{user_id}"''')
        return [Task(name, description, time, user_id, state) for name, description, time, _, state in raw]
    
    def task_change_state(self, task: Task, new_state: str):
        self.remove_task(task)
        task.state = new_state
        self.add_task(task)