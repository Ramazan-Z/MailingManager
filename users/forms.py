from typing import Any

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import ValidationError

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Класс формы  создания пользователя"""

    usable_password = None

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "avatar",
            "country",
            "password1",
            "password2",
        )

    def clean_phone_number(self) -> Any:
        """Валидация номера телефона"""
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise ValidationError("Номер должен состоять только из цифр")
        return phone_number

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Добавление стилей в инициализацию"""
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            if "Password" in str(field.label):
                field.widget.attrs["class"] = "form-control"
            else:
                field.widget.attrs.update(
                    {
                        "class": "form-control",
                        "placeholder": field.help_text,
                    }
                )
                field.help_text = ""


class UserUpdateForm(UserChangeForm):
    """Класс формы редактирования пользователя"""

    password = None

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "avatar",
            "country",
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Добавление стилей в инициализацию"""
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs.update(
                    {
                        "class": "form-control",
                        "placeholder": field.help_text,
                    }
                )
                field.help_text = ""
