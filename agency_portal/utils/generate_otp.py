
import random
from datetime import datetime,timedelta
import jwt
from decouple import config


def generate_otp():
    otp = random.randint(1000, 9000)
    return otp
def generate_token(email=None, token_time=None):
    exp_time = datetime.now() + timedelta(days=token_time)
    JWT_PAYLOAD = {
        "email": email,
        "exp": exp_time,
    }
    jwt_token = jwt.encode(JWT_PAYLOAD, config("SECRET_KEY"), algorithm="HS256")
    return jwt_token



def decode_token(token):
    payload = jwt.decode(token, config("SECRET_KEY"), algorithms="HS256")
    return payload