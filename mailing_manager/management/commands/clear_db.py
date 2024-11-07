from typing import Any

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from mailing_manager.models import Client, Mailing, MailingAttempt, Message
from users.models import CustomUser


class Command(BaseCommand):
    help = "Clear test data from data base"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Удаление существующих записей"""
        Client.objects.all().delete()
        Message.objects.all().delete()
        Mailing.objects.all().delete()
        MailingAttempt.objects.all().delete()
        Group.objects.all().delete()
        CustomUser.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("The data has been successfully deleted from the database"))
