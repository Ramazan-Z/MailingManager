from typing import Any

from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import ValidationError

from mailing_manager.forms import BootstrapMixin
from users.models import CustomUser


class CustomUserCreationForm(BootstrapMixin, UserCreationForm):
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


class UserUpdateForm(BootstrapMixin, UserChangeForm):
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
