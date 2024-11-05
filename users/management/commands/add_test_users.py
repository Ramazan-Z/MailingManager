from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создание тестовых пользователе для проекта"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        call_command("create_managers_group")
        call_command("createadmin")
        call_command("createmanager")
        call_command("createuser")
        self.stdout.write(self.style.SUCCESS("The test users is ready for use"))
