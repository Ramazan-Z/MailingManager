from django.urls import path

from mailing_manager.apps import MailingManagerConfig

from . import views

app_name = MailingManagerConfig.name

urlpatterns = [
    path("clients_list/", views.ClientsListView.as_view(), name="clients_list"),
    path("client_detail/<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path("client_add", views.ClientCreateView.as_view(), name="client_add"),
    path("client_edit/<int:pk>/", views.ClientUpdateView.as_view(), name="client_edit"),
    path("client_delete/<int:pk>/", views.ClientDeleteView.as_view(), name="client_delete"),
    path("messages_list/", views.MessagesListView.as_view(), name="messages_list"),
    path("message_detail/<int:pk>/", views.MessageDetailView.as_view(), name="message_detail"),
    path("message_add", views.MessageCreateView.as_view(), name="message_add"),
    path("message_edit/<int:pk>/", views.MessageUpdateView.as_view(), name="message_edit"),
    path("message_delete/<int:pk>/", views.MessageDeleteView.as_view(), name="message_delete"),
    path("mailings_list/", views.MailingsListView.as_view(), name="mailings_list"),
    path("mailing_detail/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing_add", views.MailingCreateView.as_view(), name="mailing_add"),
    path("mailing_edit/<int:pk>/", views.MailingUpdateView.as_view(), name="mailing_edit"),
    path("mailing_delete/<int:pk>/", views.MailingDeleteView.as_view(), name="mailing_delete"),
]
