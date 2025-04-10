from hashlib import sha256
import base64

class HashingUtil:
    @classmethod
    def hash_sha256_bytes(cls, data: str) -> bytes:
        return sha256(data.encode()).digest()
    
    @classmethod
    def hash_sha256_hex(cls, data: str) -> str:
        return sha256(data.encode()).hexdigest()
    
    @classmethod
    def hash_sha256_base64(cls, data: str) -> str:
        bytes_data = cls.hash_sha256_bytes(data)
        return base64.b64encode(bytes_data).decode()