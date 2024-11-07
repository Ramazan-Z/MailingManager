from django.core.mail import send_mail
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from mailing_manager.models import Mailing, MailingAttempt


class MailingLauncher:
    """Класс запуска рассылки"""

    def __init__(self, mailing: Mailing) -> None:
        """Инициализация экземпряра класса"""
        self.mailing = mailing

    def to_run(self) -> tuple[str, str]:
        """Запуск рассылки"""
        if self.mailing.is_blocked:
            return "Рассылка заблокирована", "not_successful"
        else:
            self.mailing.status = "running"
            if not self.mailing.date_first_message:
                self.mailing.date_first_message = timezone.now()
            server_response, status = self.send_mailing()
            self.mailing.save()
            return server_response, status

    def send_mailing(self) -> tuple[str, str]:
        """Отправка сообщения и создание попытки рассылки"""
        subject = self.mailing.message.theme
        message = self.mailing.message.text_message
        from_mail = EMAIL_HOST_USER
        recipient_list = [client.email for client in self.mailing.clients.all()]
        try:
            send_mail(subject, message, from_mail, recipient_list)
        except Exception as e:
            status = "not_successful"
            server_response = f"Ошибка отправки сообщения: {e}"
        else:
            status = "successful"
            server_response = "Сообщение успешно отправлено"
            self.mailing.date_end_message = timezone.now()
            self.mailing.status = "completed"
        finally:
            self.create_mailing_attept(status, server_response)
            return server_response, status

    def create_mailing_attept(self, status: str, server_response: str) -> None:
        """Создание попытки рассылки"""
        MailingAttempt.objects.create(
            status=status,
            server_response=server_response,
            mailing=self.mailing,
            owner=self.mailing.owner,
        )
