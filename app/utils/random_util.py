import uuid
import random
import string
import datetime

class RandomUtil:
    @classmethod
    def generate_uuid(cls) -> str:
        return str(uuid.uuid4())
    
    @classmethod
    def pick_integer(cls, min_value: int = 0, max_value: int = 100) -> int:
        return random.randint(min_value, max_value)
    
    @classmethod
    def pick_float(cls, min_value: float = 0.0, max_value: float = 1.0) -> float:
        return random.uniform(min_value, max_value)
    
    @classmethod
    def pick_string(cls, length: int = 10) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @classmethod
    def pick_boolean(cls) -> bool:
        return random.choice([True, False])
    
    @classmethod
    def pick_date(cls, start_date: datetime.date, end_date: datetime.date) -> datetime.date:
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        return start_date + datetime.timedelta(days=random_number_of_days)
    
    @classmethod
    def choose_from_list(cls, items: list):
        return random.choice(items)
    
    @classmethod
    def shuffle_list(cls, items: list) -> list:
        shuffled = items.copy()
        random.shuffle(shuffled)
        return shuffled