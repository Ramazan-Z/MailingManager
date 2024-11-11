from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from mailing_manager.models import Mailing
from mailing_manager.services import MailingLauncher


class Command(BaseCommand):
    help = "Команда запуска рассылки"

    def add_arguments(self, parser: CommandParser) -> None:
        """Добавление аргументов в команду"""
        parser.add_argument("mailing_pk", type=int)

    def handle(self, *args: Any, **options: Any) -> None:
        """Запуск рассылки"""
        mailing_pk = options["mailing_pk"]
        try:
            mailing = Mailing.objects.get(pk=mailing_pk)
        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Рассылки с ключом «{mailing_pk}» не существует"))
        else:
            mailing_launcher = MailingLauncher(mailing)
            server_response, status = mailing_launcher.to_run()
            if status == "successful":
                self.stdout.write(self.style.SUCCESS(server_response))
            else:
                self.stdout.write(self.style.ERROR(server_response))
