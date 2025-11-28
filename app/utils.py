from passlib.context import CryptContext

# Bcrypt орнына sha256_crypt қолданамыз (Бұл Render-де қатесіз істейді)
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)