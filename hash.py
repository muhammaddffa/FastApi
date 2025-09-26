from passlib.context import CryptContext

# Buat context hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Generate hash untuk "admin123"
hashed_password = get_password_hash("hr123")
print("Hash untuk admin123:", hashed_password)
