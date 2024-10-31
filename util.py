from passlib.context import CryptContext

# Initialize bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate a hashed password
def get_password_hash(plain_password):
    return pwd_context.hash(plain_password)

# Verify if a plain password matches the hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Example usage
plain_password = "passw0rd"
hashed_password = get_password_hash(plain_password)
#hashed_password = "$2b$12$MQYx6ARB9L/fymxnCOxbuOZFnydoAU9APXPDq/j8XUL9QqKhInTRO"
#hashed_password = "$2b$12$hk1raScWd58umSQbgemQ7.SJqfZksFp.tjNPxwaHMLc2znxoRWSYK"

print(f"Plain password: {plain_password}")
print(f"Hashed password: {hashed_password}")
print("Is the password correct? ", verify_password(plain_password, hashed_password))