from app.utils.hashing_util import HashingUtil

class ServiceDeleteme:
    def __init__(self):
        pass

    @staticmethod
    def sum_two_numbers(a: int, b: int) -> int:
        return a + b
    
    @staticmethod
    def subtract_two_numbers(a: int, b: int) -> int:
        return a - b
    
    @staticmethod
    def hash_data_hex(plain_text: str) -> str:
        return HashingUtil.hash_sha256_hex(plain_text)
    
    @staticmethod
    def hash_data_base64(plain_text: str) -> str:
        return HashingUtil.hash_sha256_base64(plain_text)