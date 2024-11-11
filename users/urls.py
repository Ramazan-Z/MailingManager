from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
)
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.views import (
    DeleteUserView,
    ProfileUserView,
    RecoveryPasswordView,
    RegisterView,
    UpdateUserView,
    UsersListView,
    email_confirm,
    user_block_unblock,
)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("email_confirm/<str:token>/", email_confirm, name="email_confirm"),
    path("profile/<int:pk>/", ProfileUserView.as_view(), name="profile"),
    path("edit/", UpdateUserView.as_view(), name="edit"),
    path("delete/", DeleteUserView.as_view(), name="delete"),
    path("users_list/", UsersListView.as_view(), name="users_list"),
    path("user_block/<int:pk>/", user_block_unblock, name="user_block"),
    # Востановление пароля
    path("psw_reset/", RecoveryPasswordView.as_view(), name="psw_reset"),
    path(
        "psw_reset_done/",
        PasswordResetDoneView.as_view(
            template_name="users/psw_reset_done.html",
        ),
        name="psw_reset_done",
    ),
    path(
        "psw_reset_confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/psw_reset_confirm.html",
            success_url=reverse_lazy("users:psw_reset_complete"),
        ),
        name="psw_reset_confirm",
    ),
    path(
        "psw_reset_complete/",
        PasswordResetCompleteView.as_view(
            template_name="users/psw_reset_complete.html",
        ),
        name="psw_reset_complete",
    ),
]
