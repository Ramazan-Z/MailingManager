from django.conf import settings
from django.db import models


class Client(models.Model):
    """Класс-модель сущности получателя рассылки (клиента)"""

    # Email
    email: models.Field = models.EmailField(
        unique=True,
        verbose_name="Email клиента",
        help_text="Введите Email клиента",
    )
    # Полное имя (Ф. И. О.)
    full_name: models.Field = models.CharField(
        max_length=255,
        verbose_name="Ф. И. О. клиента",
        help_text="Введите Ф. И. О. клиента",
    )
    # Коментарий
    comments: models.Field = models.TextField(
        blank=True,
        null=True,
        verbose_name="Коментарий",
        help_text="Введите коментарий",
    )
    # Владелец
    owner: models.Field = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец",
        related_name="clients",
    )

    def __str__(self) -> str:
        """Строковое представление клиента"""
        return str(self.full_name)

    class Meta:
        """Метаданные модели"""

        db_table = "clients"  # Имя таблицы в БД
        verbose_name = "Клиент"  # Отображаемое имя в ед. числе
        verbose_name_plural = "Клиенты"  # Отображаемое имя во мн. числе
        ordering = ["full_name"]  # Порядок сортировки
        permissions = [("can_view_clients", "Может просматривать чужих клиентов")]


class Message(models.Model):
    """Класс-модель сущности сообщения"""

    # Тема сообщения
    theme: models.Field = models.CharField(
        max_length=255,
        verbose_name="Тема cообщения",
        help_text="Введите тему сообщения",
    )
    # Текст сообщения
    text_message: models.Field = models.TextField(
        verbose_name="Текст сообщения",
        help_text="Введите текст сообщения",
    )
    # Владелец
    owner: models.Field = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец",
        related_name="messages",
    )

    def __str__(self) -> str:
        """Строковое представление сообщения"""
        return str(self.theme)

    class Meta:
        """Метаданные модели"""

        db_table = "messages"  # Имя таблицы в БД
        verbose_name = "Сообщение"  # Отображаемое имя в ед. числе
        verbose_name_plural = "Сообщения"  # Отображаемое имя во мн. числе
        ordering = ["theme"]  # Порядок сортировки
        permissions = [("can_view_message", "Может просматривать чужие сообщения")]


class Mailing(models.Model):
    """Класс-модель сущности рассылки"""

    # Варианты статуса
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("running", "Запущена"),
        ("completed", "Завершена"),
    ]

    # Дата и время первой отправки
    date_first_message: models.Field = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время первой отправки",
        help_text="Введите дату и время первой отправки",
    )
    # Дата и время окончания отправки
    date_end_message: models.Field = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время окончания отправки",
        help_text="Введите дату и время окончания отправки",
    )
    # Сообщение (ForeignKey)
    message: models.Field = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        verbose_name="Сообщение",
        help_text="Выберете связанное сообщение",
        related_name="mailing_messages",
    )
    # Получатели
    clients: models.Field = models.ManyToManyField(
        Client,
        verbose_name="Клиенты",
        help_text="Выберете получателей рассылки",
        related_name="mailing_clients",
    )
    # Статус
    status: models.Field = models.CharField(
        max_length=9,
        choices=STATUS_CHOICES,
        blank=True,
        default="created",
        verbose_name="Статус",
    )
    # Признак блокировки
    is_blocked: models.Field = models.BooleanField(
        default=False,
        verbose_name="Блокировка",
    )
    # Владелец
    owner: models.Field = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец",
        related_name="mailings",
    )

    def __str__(self) -> str:
        """Строковое представление рассылки"""
        return f"Рассылка для сообщения: «{self.message}»"

    class Meta:
        """Метаданные модели"""

        db_table = "mailings"  # Имя таблицы в БД
        verbose_name = "Рассылка"  # Отображаемое имя в ед. числе
        verbose_name_plural = "Рассылки"  # Отображаемое имя во мн. числе
        ordering = ["date_first_message"]  # Порядок сортировки
        permissions = [
            ("can_view_mailing", "Может просматривать чужие рассылки"),
            ("can_mailing_blocked", "Может блокировать рассылки"),
        ]


class MailingAttempt(models.Model):
    """Класс-модель сущности попытки рассылки"""

    # Варианты статуса
    STATUS_CHOICES = [
        ("successful", "Успешно"),
        ("not_successful", "Не успешно"),
    ]

    # Дата и время попытки
    date_attempt: models.Field = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки",
    )
    # Статус
    status: models.Field = models.CharField(
        max_length=14,
        choices=STATUS_CHOICES,
        verbose_name="Статус",
    )
    # Ответ почтового сервера
    server_response: models.Field = models.TextField(
        verbose_name="Ответ почтового сервера",
    )
    # Рассылка (ForeignKey)
    mailing: models.Field = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name="Рассылка",
        related_name="mailing_attempts",
    )
    # Владелец
    owner: models.Field = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец",
        related_name="attemts",
    )

    class Meta:
        """Метаданные модели"""

        db_table = "mailing_attempts"  # Имя таблицы в БД
        verbose_name = "Попытка рассылки"  # Отображаемое имя в ед. числе
        verbose_name_plural = "Попытки рассылки"  # Отображаемое имя во мн. числе
        ordering = ["date_attempt"]  # Порядок сортировки
