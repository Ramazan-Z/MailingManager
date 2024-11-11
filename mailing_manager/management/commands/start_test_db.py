from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creating and filling out a test database"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Создание и заполнение тестовой базы данных"""
        call_command("create_db")
        call_command("migrate")
        call_command("add_test_data")
        self.stdout.write(self.style.SUCCESS("The database is ready for use"))
