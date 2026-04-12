from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    default="argon2",
    argon2__default_rounds=10,
    argon2__salt_size=16,
    deprecated="auto"
)

__all__ = ("hash_password", "verify_password")

def hash_password(password: str) -> str:
    return pwd_context.hash(password) 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
