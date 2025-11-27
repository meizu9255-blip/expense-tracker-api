from passlib.context import CryptContext

# Бұл жерде bcrypt орнына SHA256-crypt қолданамыз
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Парольді алып, хешке айналдырады (SHA256 арқылы)"""
    # SHA256 ұзындықты өзі реттейді, сондықтан қысқарту қажет емес
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Енгізілген пароль мен базадағы хешті салыстырады"""
    return pwd_context.verify(plain_password, hashed_password)