from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from config.settings import CACH_ENABLED, CACH_TIME
from mailing_manager import forms, models, services


@method_decorator(cache_page(CACH_TIME), name="dispatch")
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


class AttemptsListView(LoginRequiredMixin, services.CustomListView):
    """Контроллер страницы статистики"""

    model = models.MailingAttempt
    required_permission_name = ""
    cache_key_name = "attempts"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление переменных в шаблон страницы статистики"""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["attempts_count"] = queryset.count()
        context["attempts_success_count"] = queryset.filter(status="successful").count()
        context["attempts_error_count"] = queryset.filter(status="not_successful").count()
        return context


class ClientsListView(LoginRequiredMixin, services.CustomListView):
    """Контроллер страницы со списком клиентов"""

    model = models.Client
    required_permission_name = "mailing_manager.can_view_other_client"
    cache_key_name = "clients"


class ClientDetailView(LoginRequiredMixin, services.CustomDetailView):
    """Контроллер страницы с деталями клиента"""

    model = models.Client
    required_permission_name = "mailing_manager.can_view_other_client"
    cache_key_name = "client"


class ClientCreateView(LoginRequiredMixin, services.CustomCreateView):
    """Контроллер страницы создания клиента"""

    model = models.Client
    form_class = forms.ClientForm
    success_url = reverse_lazy("mailing_manager:clients_list")


class ClientUpdateView(LoginRequiredMixin, services.CustomUpdateView):
    """Контроллер страницы редактирования клиента"""

    model = models.Client
    form_class = forms.ClientForm
    success_url = reverse_lazy("mailing_manager:clients_list")


class ClientDeleteView(services.CustomDeleteView):
    """Контроллер страницы удаления клиента"""

    model = models.Client
    template_name = "mailing_manager/delete_confirm_form.html"
    success_url = reverse_lazy("mailing_manager:clients_list")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление переменных в шаблон удаления"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Удаление клиента"
        context["question"] = f"Вы уверены что хотите удалить клиента «{self.object.full_name}»?"
        context["back"] = reverse_lazy("mailing_manager:client_detail", args=[self.kwargs.get("pk")])
        return context


class MessagesListView(LoginRequiredMixin, services.CustomListView):
    """Контроллер страницы со списком сообщений"""

    model = models.Message
    required_permission_name = "mailing_manager.can_view_other_message"
    cache_key_name = "messages"


class MessageDetailView(LoginRequiredMixin, services.CustomDetailView):
    """Контроллер страницы с деталями сообщения"""

    model = models.Message
    required_permission_name = "mailing_manager.can_view_other_message"
    cache_key_name = "message"


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Контроллер страницы создания сообщения"""

    model = models.Message
    form_class = forms.MessageForm
    success_url = reverse_lazy("mailing_manager:messages_list")

    def form_valid(self, form: forms.ClientForm) -> HttpResponse:
        """Сохранение формсета с установкой владельца"""
        if CACH_ENABLED:
            cache.clear()  # Очистка кэш
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


class MessageUpdateView(LoginRequiredMixin, services.CustomUpdateView):
    """Контроллер страницы редактирования сообщения"""

    model = models.Message
    form_class = forms.MessageForm
    success_url = reverse_lazy("mailing_manager:messages_list")


class MessageDeleteView(services.CustomDeleteView):
    """Контроллер страницы удаления сообщения"""

    model = models.Message
    template_name = "mailing_manager/delete_confirm_form.html"
    success_url = reverse_lazy("mailing_manager:messages_list")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление переменных в шаблон удаления"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Удаление сообщения"
        context["question"] = f"Вы уверены что хотите удалить сообщение «{self.object.theme}»?"
        context["back"] = reverse_lazy("mailing_manager:message_detail", args=[self.kwargs.get("pk")])
        return context


class MailingsListView(LoginRequiredMixin, services.CustomListView):
    """Контроллер страницы со списком рассылок"""

    model = models.Mailing
    required_permission_name = "mailing_manager.can_view_other_mailing"
    cache_key_name = "mailings"


class MailingDetailView(LoginRequiredMixin, services.CustomDetailView):
    """Контроллер страницы с деталями рассылки"""

    model = models.Mailing
    required_permission_name = "mailing_manager.can_view_other_mailing"
    cache_key_name = "mailing"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление получателей в шаблон для отображения"""
        context = super().get_context_data(**kwargs)
        context["clients"] = self.object.clients.values()
        return context


class MailingCreateView(LoginRequiredMixin, services.CustomCreateView):
    """Контроллер страницы создания рассылки"""

    model = models.Mailing
    form_class = forms.MailingForm
    success_url = reverse_lazy("mailing_manager:mailings_list")


class MailingUpdateView(LoginRequiredMixin, services.CustomUpdateView):
    """Контроллер страницы редактирования рассылки"""

    model = models.Mailing
    form_class = forms.MailingForm
    success_url = reverse_lazy("mailing_manager:mailings_list")


class MailingDeleteView(services.CustomDeleteView):
    """Контроллер страницы удаления рассылки"""

    model = models.Mailing
    template_name = "mailing_manager/delete_confirm_form.html"
    success_url = reverse_lazy("mailing_manager:mailings_list")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавление переменных в шаблон удаления"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Удаление рассылки"
        context["question"] = f"Вы уверены что хотите удалить рассылку «{self.object}»?"
        context["back"] = reverse_lazy("mailing_manager:mailing_detail", args=[self.kwargs.get("pk")])
        return context


def mailing_block_unblock(request: HttpRequest, pk: int) -> HttpResponse:
    """Контроллер страницы блокировки рассылки"""
    if CACH_ENABLED:
        cache.clear()  # Очистка кэш
    user = request.user
    mailing = get_object_or_404(models.Mailing, pk=pk)
    if hasattr(user, "has_perm") and user.has_perm("mailing_manager.can_mailing_blocked"):
        mailing.is_blocked = not mailing.is_blocked
        mailing.save()
    return redirect(reverse_lazy("mailing_manager:mailings_list"))


def mailing_start(request: HttpRequest, pk: int) -> HttpResponse:
    """Контроллер страницы запуска рассылки"""
    if CACH_ENABLED:
        cache.clear()  # Очистка кэш
    mailing = get_object_or_404(models.Mailing, pk=pk)
    if mailing.owner == request.user and not mailing.is_blocked:
        mailing_launcher = services.MailingLauncher(mailing)
        mailing_launcher.to_run()
    return redirect(reverse_lazy("mailing_manager:mailings_list"))
