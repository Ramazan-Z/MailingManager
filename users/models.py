from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Класс сущности пользователя"""

    # Email
    email: models.EmailField = models.EmailField(
        unique=True,
        verbose_name="Эл. почта",
        help_text="Введите эл. почту",
    )
    # Аватар
    avatar: models.Field = models.ImageField(
        upload_to="avatars/",
        verbose_name="Аватар",
        blank=True,
        null=True,
        help_text="Загрузите аватар",
    )
    # Номер телефона
    phone_number: models.Field = models.CharField(
        max_length=15,
        verbose_name="Телефон",
        blank=True,
        null=True,
        help_text="Введите номер телефона",
    )
    # Страна
    country: models.Field = models.CharField(
        max_length=60,
        verbose_name="Страна",
        blank=True,
        null=True,
        help_text="Введите страну",
    )
    # Токен подтверждения почты
    token: models.Field = models.CharField(
        max_length=100,
        verbose_name="Токен",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        """Строковое представление пользователя"""
        return str(self.email)

    class Meta:
        """Метаданные модели"""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]
