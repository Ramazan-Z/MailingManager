import secrets

from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER
from users.models import CustomUser


def send_confirm_email(user: CustomUser, host: str) -> str:
    """Отправка сообщения для подтверждения почты"""
    token = secrets.token_hex(16)
    subject = "Подтверждение Email"
    message = "Для подтверждения Email перейдите по ссылке:\n" f"http://{host}/users/email_confirm/{token}/"
    recipient_list = [user.email]
    send_mail(subject, message, EMAIL_HOST_USER, recipient_list)
    return token
