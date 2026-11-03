from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """Allow authentication with either username or email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username or kwargs.get("email", "")
        if not identifier or not password:
            return None

        try:
            if "@" in identifier:
                user = UserModel.objects.get(email__iexact=identifier)
            else:
                user = UserModel.objects.get(username__iexact=identifier)
        except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
            # Keep the timing close to a real password check and never reveal
            # whether a duplicate or missing identity exists.
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None