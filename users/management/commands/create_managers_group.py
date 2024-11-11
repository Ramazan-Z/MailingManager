from typing import Any

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создание группы с правами менеджера"

    def handle(self, *args: Any, **options: Any) -> None:
        managers_group = Group.objects.create(name="Managers")

        user_block_permission = Permission.objects.get(codename="can_block_user")
        client_permission = Permission.objects.get(codename="can_view_other_client")
        message_permission = Permission.objects.get(codename="can_view_other_message")
        mailing_permission = Permission.objects.get(codename="can_view_other_mailing")
        mailing_blocked_permission = Permission.objects.get(codename="can_mailing_blocked")

        managers_group.permissions.add(
            user_block_permission,
            client_permission,
            message_permission,
            mailing_permission,
            mailing_blocked_permission,
        )

        managers_group.save()
        self.stdout.write(self.style.SUCCESS("Successfully created managers group"))
