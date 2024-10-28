from django.contrib import admin

from .models import Client, Mailing, MailingAttempt, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Регистрация модели клиентов в админке"""

    list_display = ("id", "full_name", "email")
    search_fields = ("full_name",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Регистрация модели сообщений в админке"""

    list_display = ("id", "theme")
    search_fields = ("theme",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Регистрация модели рассылки в админке"""

    list_display = ("id", "message", "status")
    list_filter = ("status",)
    search_fields = ("message",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Регистрация модели попытки рассылки в админке"""

    list_display = ("id", "date_attempt", "mailing", "status")
    list_filter = ("status",)
    search_fields = ("mailing",)
