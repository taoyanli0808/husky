
import uuid
import random

def get_husky_id(prefix=None):
    magic = random.randint(10000, 99999)
    id = f"{prefix}-{str(uuid.uuid4())[:8].upper()}-{magic}"
    return id
