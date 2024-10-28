from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Регистрация модели пользователя в админке"""

    list_display = ("email", "username")
    list_filter = ("country",)
    search_fields = ("username",)
