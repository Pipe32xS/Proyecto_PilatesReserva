from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Permite autenticarse con username O con email (case-insensitive).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            if "@" in (username or ""):
                user = UserModel.objects.get(email__iexact=username)
            else:
                user = UserModel.objects.get(username__iexact=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
