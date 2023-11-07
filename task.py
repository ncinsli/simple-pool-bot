from dataclasses import dataclass
from datetime import time

from user import User

@dataclass
class Task:
    name: str
    description: str
    time: time
    user_id: str
    state: str