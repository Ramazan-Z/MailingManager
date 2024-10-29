from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from . import forms, models


class ClientsListView(ListView):
    """Контроллер страницы со списком клиентов"""

    model = models.Client


class ClientDetailView(DetailView):
    """Контроллер страницы с деталями клиента"""

    model = models.Client


class ClientCreateView(CreateView):
    """Контроллер страницы создания клиента"""

    model = models.Client
    form_class = forms.ClientForm
    success_url = reverse_lazy("mailing_manager:clients_list")


class ClientUpdateView(UpdateView):
    """Контроллер страницы редактирования клиента"""

    model = models.Client
    form_class = forms.ClientForm
    success_url = reverse_lazy("mailing_manager:clients_list")


class ClientDeleteView(DeleteView):
    """Контроллер страницы удаления клиента"""

    model = models.Client
    success_url = reverse_lazy("mailing_manager:clients_list")


class MessagesListView(ListView):
    """Контроллер страницы со списком сообщений"""

    model = models.Message


class MessageDetailView(DetailView):
    """Контроллер страницы с деталями сообщения"""

    model = models.Message


class MessageCreateView(CreateView):
    """Контроллер страницы создания сообщения"""

    model = models.Message
    form_class = forms.MessageForm
    success_url = reverse_lazy("mailing_manager:messages_list")


class MessageUpdateView(UpdateView):
    """Контроллер страницы редактирования сообщения"""

    model = models.Message
    form_class = forms.MessageForm
    success_url = reverse_lazy("mailing_manager:messages_list")


class MessageDeleteView(DeleteView):
    """Контроллер страницы удаления сообщения"""

    model = models.Message
    success_url = reverse_lazy("mailing_manager:messages_list")


class MailingsListView(ListView):
    """Контроллер страницы со списком рассылок"""

    model = models.Mailing


class MailingDetailView(DetailView):
    """Контроллер страницы с деталями рассылки"""

    model = models.Mailing


class MailingCreateView(CreateView):
    """Контроллер страницы создания рассылки"""

    model = models.Mailing
    form_class = forms.MailingForm
    success_url = reverse_lazy("mailing_manager:mailings_list")


class MailingUpdateView(UpdateView):
    """Контроллер страницы редактирования рассылки"""

    model = models.Mailing
    form_class = forms.MailingForm
    success_url = reverse_lazy("mailing_manager:mailings_list")


class MailingDeleteView(DeleteView):
    """Контроллер страницы удаления рассылки"""

    model = models.Mailing
    success_url = reverse_lazy("mailing_manager:mailings_list")
