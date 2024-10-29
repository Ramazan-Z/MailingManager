from typing import Any

from django import forms

from .models import Client, Mailing, Message


class ClientForm(forms.ModelForm):
    """Класс формы клиента"""

    class Meta:
        """Метаданные формы"""

        model = Client
        fields = ["full_name", "email", "comments"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Добавление стилей в инициализацию"""
        super(ClientForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.help_text,
                }
            )
            field.help_text = ""


class MessageForm(forms.ModelForm):
    """Класс формы сообщения"""

    class Meta:
        """Метаданные формы"""

        model = Message
        fields = ["theme", "text_message"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Добавление стилей в инициализацию"""
        super(MessageForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.help_text,
                }
            )
            field.help_text = ""


class MailingForm(forms.ModelForm):
    """Класс формы рассылки"""

    class Meta:
        """Метаданные формы"""

        model = Mailing
        fields = ["message", "clients"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Добавление стилей в инициализацию"""
        super(MailingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.help_text,
                }
            )
            field.help_text = ""
