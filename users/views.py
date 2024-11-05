from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from users import services
from users.forms import CustomUserCreationForm, UserUpdateForm
from users.models import CustomUser


class RegisterView(CreateView):
    """Контроллер страницы регистрации пользователя"""

    template_name = "users/user_form.html"
    form_class = CustomUserCreationForm
    context_object_name = "user_obj"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form: CustomUserCreationForm) -> HttpResponse:
        """Логика регистрации с подтверждением почты"""
        user = form.save()
        host = self.request.get_host()
        token = services.send_confirm_email(user, host)
        user.is_active = False
        user.token = token
        user.save()
        return super().form_valid(form)


def email_confirm(request: HttpRequest, token: str) -> HttpResponse:
    """Контроллер страницы подтверждения почты"""
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse_lazy("users:login"))


class ProfileUserView(LoginRequiredMixin, DetailView):
    """Контроллер страницы просмотра профиля"""

    model = CustomUser
    template_name = "users/profile.html"

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Проверка прав пользователя на просмотр профиля"""
        self.object = super().get_object(queryset)
        user = self.request.user
        if hasattr(user, "has_perm") and user.has_perm("users.can_block_user") or self.object == user:
            return self.object
        raise PermissionDenied


class UpdateUserView(LoginRequiredMixin, UpdateView):
    """Контроллер страницы редактирования профиля"""

    template_name = "users/user_form.html"
    form_class = UserUpdateForm
    context_object_name = "user_obj"

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Получение пользователя в качестве объекта"""
        return self.request.user

    def get_success_url(self) -> Any:
        """Переопределение метода"""
        return reverse_lazy("users:profile", args=[self.object.pk])


class DeleteUserView(DeleteView):
    """Контроллер страницы удаления аккаунта"""

    template_name = "users/delete_confirm_form.html"
    success_url = reverse_lazy("mailing_manager:home")

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Получение пользователя в качестве объекта"""
        return self.request.user

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Редирект на авторизацию анонимных юзеров"""
        if self.request.user:
            return super().get(request, *args, **kwargs)
        return redirect(reverse_lazy("users:login"))


class RecoveryPasswordView(PasswordResetView):
    """Контроллер страницы востановления пароля"""

    template_name = "users/psw_reset_form.html"
    email_template_name = "users/psw_reset_email.html"
    subject_template_name = "users/psw_reset_subject.txt"
    success_url = reverse_lazy("users:psw_reset_done")


class UsersListView(ListView):
    """Контроллер страницы списка пользователей сервиса"""

    model = CustomUser
    template_name = "users/users_list.html"

    def get_queryset(self) -> Any:
        """Проверка прав пользователя на просмотр клиентов"""
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, "has_perm") and user.has_perm("users.can_block_user"):
            return queryset
        raise PermissionDenied


def user_block_unblock(request: HttpRequest, pk: int) -> HttpResponse:
    """Контроллер страницы блокировки пользователя"""
    user = request.user
    blocked_user = get_object_or_404(CustomUser, pk=pk)
    if (
        hasattr(user, "has_perm")
        and user.has_perm("users.can_block_user")
        and not blocked_user.has_perm("users.can_block_user")
    ):
        blocked_user.is_active = not blocked_user.is_active
        blocked_user.save()
    return redirect(reverse_lazy("users:users_list"))
