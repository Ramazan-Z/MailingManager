import os
from typing import Any

from django.core.management.base import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    help = "Создание пользователя с правами администратора"

    def handle(self, *args: Any, **options: Any) -> None:
        user = CustomUser.objects.create(
            email=os.getenv("ADMIN_EMAIL"),
            username=os.getenv("ADMIN_USERNAME"),
        )
        user.set_password(os.getenv("ADMIN_PASSWORD"))
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Successfully created admin user with email {user.email}"))
