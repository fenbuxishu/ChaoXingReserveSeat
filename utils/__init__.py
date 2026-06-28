import os
from .encrypt import AES_Encrypt, generate_captcha_key, verify_param_seatengine
from .reserve import reserve

def get_user_credentials(action):
    usernames = os.environ.get('USERNAMES', '') if action else ''
    passwords = os.environ.get('PASSWORDS', '') if action else ''
    return usernames, passwords
