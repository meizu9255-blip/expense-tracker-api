from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"], 
    default="pbkdf2_sha256", 
    pbkdf2_sha256__rounds=1000
)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)