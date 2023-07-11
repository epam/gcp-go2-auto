from cryptography.fernet import Fernet
import secrets;

fernet_key = Fernet.generate_key()
print(f'Fernet Key: {fernet_key.decode()}')
print(f'Webserver Secret Key: {secrets.token_hex(16)}')
