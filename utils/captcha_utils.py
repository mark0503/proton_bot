import base64
import random

from captcha.image import ImageCaptcha


def create_random_captcha_text():
    nonce = ''
    for i in range(6):
        # AM: такие штуки можно делать через модуль string - напр., string.ascii_letters + string.digits
        nonce += "0123456789"[
            int(7 * random.random())
        ]
        return nonce


def create_image_captcha(captcha_text):
    image_captcha = ImageCaptcha()
    captcha = base64.b64encode(image_captcha.generate(captcha_text).getvalue())
    return captcha
