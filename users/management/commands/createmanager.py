import os
from typing import Any

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    help = "Создание пользователя с правами менеджера"

    def handle(self, *args: Any, **options: Any) -> None:
        user = CustomUser.objects.create(
            email=os.getenv("MANAGER_EMAIL"),
            username=os.getenv("MANAGER_USERNAME"),
        )
        user.set_password(os.getenv("MANAGER_PASSWORD"))
        moderators_group = Group.objects.get(name="Managers")
        user.groups.add(moderators_group)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Successfully created manager user with email {user.email}"))
