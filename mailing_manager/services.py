from typing import Any

from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from config.settings import CACH_ENABLED, CACH_TIME, EMAIL_HOST_USER
from mailing_manager.models import Mailing, MailingAttempt


class CacheMixin:
    """Класс-миксин для работы с кэшем"""

    cache_key_name: str
    kwargs: dict[str, Any]

    @staticmethod
    def get_cache_data(cache_key_name: str) -> Any:
        if CACH_ENABLED:
            return cache.get(cache_key_name)

    @staticmethod
    def set_cache_data(data: Any, cache_key_name: str) -> None:
        if CACH_ENABLED:
            cache.set(cache_key_name, data, CACH_TIME)

    @staticmethod
    def clear_cache_data() -> None:
        if CACH_ENABLED:
            cache.clear()

    def get_key_name(self) -> str:
        return f"{self.cache_key_name}/{self.kwargs.get('pk')}"


class CustomListView(CacheMixin, ListView):
    """Кастомный класс представления с кэшированием и правами доступа"""

    required_permission_name: str

    def get_queryset(self) -> Any:
        """Кэширование и проверка прав доступа"""
        queryset = self.get_cache_data(self.cache_key_name)
        if queryset:
            return queryset
        queryset = super().get_queryset()
        user = self.request.user
        if not (hasattr(user, "has_perm") and user.has_perm(self.required_permission_name)):
            queryset = queryset.filter(owner=user)
        self.set_cache_data(queryset, self.cache_key_name)  # Установка кэш
        return queryset


class CustomDetailView(CacheMixin, DetailView):
    """Кастомный класс представления с кэшированием и правами доступа"""

    required_permission_name: str

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Кэширование и проверка прав доступа"""
        object_detail = self.get_cache_data(self.get_key_name())
        if not object_detail:
            object_detail = super().get_object(queryset)
            self.set_cache_data(object_detail, self.get_key_name())  # Установка кэш
        user = self.request.user
        if hasattr(user, "has_perm") and user.has_perm(self.required_permission_name) or object_detail.owner == user:
            return object_detail
        raise PermissionDenied


class CustomCreateView(CacheMixin, CreateView):
    """Кастомный класс представления с кэшированием и правами доступа"""

    def form_valid(self, form: ModelForm) -> HttpResponse:
        """Установка текущего пользователя владельцем объекта"""
        self.clear_cache_data()  # Очистка кэш
        created_object = form.save()
        created_object.owner = self.request.user
        created_object.save()
        return super().form_valid(form)


class CustomUpdateView(CacheMixin, UpdateView):
    """Кастомный класс представления с кэшированием и правами доступа"""

    def get_form_class(self) -> Any:
        """Ограничение редактирования объекта только владельцу"""
        self.clear_cache_data()  # Очистка кэш
        if self.request.user == self.object.owner:
            return self.form_class
        raise PermissionDenied


class CustomDeleteView(DeleteView):
    """Кастомный класс представления с кэшированием и правами доступа"""

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Ограничение удаления объекта только владельцу"""
        if CACH_ENABLED:
            cache.clear()  # Очистка кэш
        object_delete = super().get_object(queryset)
        if self.request.user == object_delete.owner:
            return object_delete
        raise PermissionDenied


class MailingLauncher:
    """Класс запуска рассылки"""

    def __init__(self, mailing: Mailing) -> None:
        """Инициализация экземпряра класса"""
        self.mailing = mailing

    def to_run(self) -> tuple[str, str]:
        """Запуск рассылки"""
        if self.mailing.is_blocked:
            return "Рассылка заблокирована", "not_successful"
        else:
            self.mailing.status = "running"
            if not self.mailing.date_first_message:
                self.mailing.date_first_message = timezone.now()
            server_response, status = self.send_mailing()
            self.mailing.save()
            return server_response, status

    def send_mailing(self) -> tuple[str, str]:
        """Отправка сообщения и создание попытки рассылки"""
        subject = self.mailing.message.theme
        message = self.mailing.message.text_message
        from_mail = EMAIL_HOST_USER
        recipient_list = [client.email for client in self.mailing.clients.all()]
        status = "successful"
        server_response = "Сообщение успешно отправлено"
        try:
            send_mail(subject, message, from_mail, recipient_list)
            self.mailing.date_end_message = timezone.now()
            self.mailing.status = "completed"
        except Exception as e:
            status = "not_successful"
            server_response = f"Ошибка отправки сообщения: {e}"
        finally:
            self.create_mailing_attept(status, server_response)
            return server_response, status

    def create_mailing_attept(self, status: str, server_response: str) -> None:
        """Создание попытки рассылки"""
        MailingAttempt.objects.create(
            status=status,
            server_response=server_response,
            mailing=self.mailing,
            owner=self.mailing.owner,
        )
