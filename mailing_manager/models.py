from django.db import models


class Client(models.Model):
    """Класс-модель сущности получателя рассылки (клиента)"""

    # Email
    email: models.Field = models.EmailField(
        unique=True, verbose_name="Email клиента", help_text="Введите Email клиента"
    )
    # Полное имя (Ф. И. О.)
    full_name: models.Field = models.CharField(
        max_length=255, verbose_name="Ф. И. О. клиента", help_text="Введите Ф. И. О. клиента"
    )
    # Коментарий
    comments: models.Field = models.TextField(
        verbose_name="Коментарий", blank=True, null=True, help_text="Введите коментарий"
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


class Message(models.Model):
    """Класс-модель сущности сообщения"""

    # Тема сообщения
    theme: models.Field = models.CharField(
        max_length=255, verbose_name="Тема cообщения", help_text="Введите тему сообщения"
    )
    # Текст сообщения
    text_message: models.Field = models.TextField(verbose_name="Текст сообщения", help_text="Введите текст сообщения")

    def __str__(self) -> str:
        """Строковое представление сообщения"""
        return str(self.theme)

    class Meta:
        """Метаданные модели"""

        db_table = "messages"  # Имя таблицы в БД
        verbose_name = "Сообщение"  # Отображаемое имя в ед. числе
        verbose_name_plural = "Сообщения"  # Отображаемое имя во мн. числе
        ordering = ["theme"]  # Порядок сортировки


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
        verbose_name="Дата и время первой отправки", blank=True, null=True
    )
    # Дата и время окончания отправки
    date_end_message: models.Field = models.DateTimeField(
        verbose_name="Дата и время окончания отправки", blank=True, null=True
    )
    # Сообщение (ForeignKey)
    message: models.Field = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="mailing_message")
    # Получатели
    clients: models.Field = models.ManyToManyField(Client, related_name="mailing_clients")
    # Статус
    status: models.Field = models.CharField(
        max_length=9, choices=STATUS_CHOICES, blank=True, default="created", verbose_name="Статус"
    )

    def __str__(self) -> str:
        """Строковое представление рассылки"""
        return f"Mailing for the message: «{self.message}»"

    class Meta:
        """Метаданные модели"""

        db_table = "mailings"  # Имя таблицы в БД
        verbose_name = "Рассылка"  # Отображаемое имя в ед. числе
        verbose_name_plural = "Рассылки"  # Отображаемое имя во мн. числе
        ordering = ["date_first_message"]  # Порядок сортировки


class MailingAttempt(models.Model):
    """Класс-модель сущности попытки рассылки"""

    # Варианты статуса
    STATUS_CHOICES = [
        ("successful", "Успешно"),
        ("not_successful", "Не успешно"),
    ]

    # Дата и время попытки
    date_attempt: models.Field = models.DateTimeField(auto_now_add=True)
    # Статус
    status: models.Field = models.CharField(max_length=14, choices=STATUS_CHOICES, verbose_name="Статус")
    # Ответ почтового сервера
    server_response: models.Field = models.TextField(verbose_name="Ответ почтового сервера")
    # Рассылка (ForeignKey)
    mailing: models.Field = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="mailing_attempts")

    class Meta:
        """Метаданные модели"""

        db_table = "mailing_attempts"  # Имя таблицы в БД
        verbose_name = "Попытка рассылки"  # Отображаемое имя в ед. числе
        verbose_name_plural = "Попытки рассылки"  # Отображаемое имя во мн. числе
        ordering = ["date_attempt"]  # Порядок сортировки
