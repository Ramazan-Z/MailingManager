from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.forms.models import ModelFormMetaclass
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from mailing_manager import forms, models
from mailing_manager.services import MailingLauncher


class HomeTemplateView(TemplateView):
    """Контроллер домашней страницы"""

    template_name = "mailing_manager/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление переменных в шаблон главной страницы"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            clients = models.Client.objects.filter(owner=user)
            mailings = models.Mailing.objects.filter(owner=user)
            context["clients_count"] = clients.count()
            context["mailings_count"] = mailings.count()
            context["active_mailings_count"] = mailings.filter(status="running").count()
            context["completed_mailings_count"] = mailings.filter(status="completed").count()
        return context


class AttemptsListView(LoginRequiredMixin, ListView):
    """Контроллер страницы статистики"""

    model = models.MailingAttempt

    def get_queryset(self) -> Any:
        """Проверка прав пользователя на просмотр попыток рассылки"""
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление переменных в шаблон страницы статистики"""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["attempts_count"] = queryset.count()
        context["attempts_success_count"] = queryset.filter(status="successful").count()
        context["attempts_error_count"] = queryset.filter(status="not_successful").count()
        return context


class ClientsListView(LoginRequiredMixin, ListView):
    """Контроллер страницы со списком клиентов"""

    model = models.Client

    def get_queryset(self) -> Any:
        """Проверка прав пользователя на просмотр клиентов"""
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, "has_perm") and user.has_perm("mailing_manager.can_view_other_client"):
            return queryset
        return queryset.filter(owner=user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    """Контроллер страницы с деталями клиента"""

    model = models.Client

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Проверка прав пользователя на просмотр клиента"""
        client = super().get_object(queryset)
        user = self.request.user
        if (
            hasattr(user, "has_perm")
            and user.has_perm("mailing_manager.can_view_other_client")
            or client.owner == user
        ):
            return client
        raise PermissionDenied


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Контроллер страницы создания клиента"""

    model = models.Client
    form_class = forms.ClientForm
    success_url = reverse_lazy("mailing_manager:clients_list")

    def form_valid(self, form: forms.ClientForm) -> HttpResponse:
        """Установка текущего пользователя владельцем клиента"""
        client = form.save()
        client.owner = self.request.user
        client.save()
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Контроллер страницы редактирования клиента"""

    model = models.Client
    form_class = forms.ClientForm
    success_url = reverse_lazy("mailing_manager:clients_list")

    def get_form_class(self) -> ModelFormMetaclass:
        """Ограничение редактирования клиента только владельцу"""
        if self.request.user == self.object.owner:
            return forms.ClientForm
        raise PermissionDenied


class ClientDeleteView(DeleteView):
    """Контроллер страницы удаления клиента"""

    model = models.Client
    template_name = "mailing_manager/delete_confirm_form.html"
    success_url = reverse_lazy("mailing_manager:clients_list")

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Ограничение удаления клиента только владельцу"""
        client = super().get_object(queryset)
        if self.request.user == client.owner:
            return client
        raise PermissionDenied

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление переменных в шаблон удаления"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Удаление клиента"
        context["question"] = f"Вы уверены что хотите удалить клиента «{self.object.full_name}»?"
        context["back"] = reverse_lazy("mailing_manager:client_detail", args=[self.kwargs.get("pk")])
        return context


class MessagesListView(LoginRequiredMixin, ListView):
    """Контроллер страницы со списком сообщений"""

    model = models.Message

    def get_queryset(self) -> Any:
        """Проверка прав пользователя на просмотр сообщений"""
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, "has_perm") and user.has_perm("mailing_manager.can_view_other_message"):
            return queryset
        return queryset.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Контроллер страницы с деталями сообщения"""

    model = models.Message

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Проверка прав пользователя на просмотр сообщения"""
        message = super().get_object(queryset)
        user = self.request.user
        if (
            hasattr(user, "has_perm")
            and user.has_perm("mailing_manager.can_view_other_message")
            or message.owner == user
        ):
            return message
        raise PermissionDenied


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Контроллер страницы создания сообщения"""

    model = models.Message
    form_class = forms.MessageForm
    success_url = reverse_lazy("mailing_manager:messages_list")

    def form_valid(self, form: forms.ClientForm) -> HttpResponse:
        """Сохранение формсета с установкой владельца"""
        context_data = self.get_context_data()
        formset = context_data["formset"]
        if form.is_valid() and formset.is_valid():
            message = form.save()
            # Установка владельца сообщения
            message.owner = self.request.user
            formset.instance = message
            mailing_lst = formset.save()
            # Установка владельца связанной рассылки
            for mailing in mailing_lst:
                mailing.owner = self.request.user
                mailing.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление формсета в шаблонные переменные"""
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context["formset"] = forms.MailingFormset(self.request.POST, instance=self.object)
        else:
            context["formset"] = forms.MailingFormset(instance=self.object)
        return context


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Контроллер страницы редактирования сообщения"""

    model = models.Message
    form_class = forms.MessageForm
    success_url = reverse_lazy("mailing_manager:messages_list")

    def get_form_class(self) -> ModelFormMetaclass:
        """Ограничение редактирования сообщения только владельцу"""
        if self.request.user == self.object.owner:
            return forms.MessageForm
        raise PermissionDenied


class MessageDeleteView(DeleteView):
    """Контроллер страницы удаления сообщения"""

    model = models.Message
    template_name = "mailing_manager/delete_confirm_form.html"
    success_url = reverse_lazy("mailing_manager:messages_list")

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Ограничение удаления сообщения только владельцу"""
        message = super().get_object(queryset)
        if self.request.user == message.owner:
            return message
        raise PermissionDenied

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление переменных в шаблон удаления"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Удаление сообщения"
        context["question"] = f"Вы уверены что хотите удалить сообщение «{self.object.theme}»?"
        context["back"] = reverse_lazy("mailing_manager:message_detail", args=[self.kwargs.get("pk")])
        return context


class MailingsListView(LoginRequiredMixin, ListView):
    """Контроллер страницы со списком рассылок"""

    model = models.Mailing

    def get_queryset(self) -> Any:
        """Проверка прав пользователя на просмотр рассылок"""
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, "has_perm") and user.has_perm("mailing_manager.can_view_other_mailing"):
            return queryset
        return queryset.filter(owner=user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    """Контроллер страницы с деталями рассылки"""

    model = models.Mailing

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Проверка прав пользователя на просмотр рассылки"""
        mailing = super().get_object(queryset)
        user = self.request.user
        if (
            hasattr(user, "has_perm")
            and user.has_perm("mailing_manager.can_view_other_mailing")
            or mailing.owner == user
        ):
            return mailing
        raise PermissionDenied

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление получателей в шаблон для отображения"""
        context = super().get_context_data(**kwargs)
        context["clients"] = self.object.clients.values()
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Контроллер страницы создания рассылки"""

    model = models.Mailing
    form_class = forms.MailingForm
    success_url = reverse_lazy("mailing_manager:mailings_list")

    def form_valid(self, form: forms.ClientForm) -> HttpResponse:
        """Установка текущего пользователя владельцем рассылки"""
        mailing = form.save()
        mailing.owner = self.request.user
        mailing.save()
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Контроллер страницы редактирования рассылки"""

    model = models.Mailing
    form_class = forms.MailingForm
    success_url = reverse_lazy("mailing_manager:mailings_list")

    def get_form_class(self) -> ModelFormMetaclass:
        """Ограничение редактирования рассылки только владельцу"""
        if self.request.user == self.object.owner:
            return forms.MailingForm
        raise PermissionDenied


class MailingDeleteView(DeleteView):
    """Контроллер страницы удаления рассылки"""

    model = models.Mailing
    template_name = "mailing_manager/delete_confirm_form.html"
    success_url = reverse_lazy("mailing_manager:mailings_list")

    def get_object(self, queryset: QuerySet[Any, Any] | None = None) -> Any:
        """Ограничение удаления рассылки только владельцу"""
        mailing = super().get_object(queryset)
        if self.request.user == mailing.owner:
            return mailing
        raise PermissionDenied

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление переменных в шаблон удаления"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Удаление рассылки"
        context["question"] = f"Вы уверены что хотите удалить рассылку «{self.object}»?"
        context["back"] = reverse_lazy("mailing_manager:mailing_detail", args=[self.kwargs.get("pk")])
        return context


def mailing_block_unblock(request: HttpRequest, pk: int) -> HttpResponse:
    """Контроллер страницы блокировки рассылки"""
    user = request.user
    mailing = get_object_or_404(models.Mailing, pk=pk)
    if hasattr(user, "has_perm") and user.has_perm("mailing_manager.can_mailing_blocked"):
        mailing.is_blocked = not mailing.is_blocked
        mailing.save()
    return redirect(reverse_lazy("mailing_manager:mailings_list"))


def mailing_start(request: HttpRequest, pk: int) -> HttpResponse:
    """Контроллер страницы запуска рассылки"""
    mailing = get_object_or_404(models.Mailing, pk=pk)
    if mailing.owner == request.user and not mailing.is_blocked:
        mailing_launcher = MailingLauncher(mailing)
        mailing_launcher.to_run()
    return redirect(reverse_lazy("mailing_manager:mailings_list"))
