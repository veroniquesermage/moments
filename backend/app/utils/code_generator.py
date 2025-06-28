import secrets
import string

def generate_random_code(length: int = 10) -> str:
    alphabet = string.ascii_letters  # Majuscules + minuscules
    return ''.join(secrets.choice(alphabet) for _ in range(length))
