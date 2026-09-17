import hashlib
from database import create_user, get_user

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password, email="", phone="", role="patient"):
    return create_user(username, hash_password(password), email, phone, role)

def login(username, password):
    return get_user(username, hash_password(password))
