from typing import Any

from django import forms
from django.forms.fields import Field
from django.forms.models import inlineformset_factory

from mailing_manager.models import Client, Mailing, Message


class BootstrapMixin:
    """Класс-миксин для добавления стилей к формам"""

    fields: dict[str, Field]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Добавление стилей в инициализацию"""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            elif "Password" not in str(field.label):
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.help_text
                field.help_text = ""
            else:
                field.widget.attrs["class"] = "form-control"
            if isinstance(field, forms.DateTimeField):
                field.widget.attrs["type"] = "datetime-local"


class ClientForm(BootstrapMixin, forms.ModelForm):
    """Класс формы клиента"""

    class Meta:
        model = Client
        fields = ["full_name", "email", "comments"]


class MessageForm(BootstrapMixin, forms.ModelForm):
    """Класс формы сообщения"""

    class Meta:
        model = Message
        fields = ["theme", "text_message"]


class MailingForm(BootstrapMixin, forms.ModelForm):
    """Класс формы рассылки"""

    class Meta:
        model = Mailing
        fields = ["date_first_message", "date_end_message", "message", "clients"]


# Формсет почтовой рассылки
MailingFormset = inlineformset_factory(Message, Mailing, MailingForm, extra=1)
