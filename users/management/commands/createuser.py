import os
from typing import Any

from django.core.management.base import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    help = "Создание обычного пользователя"

    def handle(self, *args: Any, **options: Any) -> None:
        user = CustomUser.objects.create(
            email=os.getenv("USER_EMAIL"),
            username=os.getenv("USER_USERNAME"),
        )
        user.set_password(os.getenv("USER_PASSWORD"))
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Successfully created user with email {user.email}"))
