from typing import Type  # noqa: UP035

from django.contrib.auth.models import AbstractUser, Group, UserManager
from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


# API-only users
# -----------------------


class APIUserManager(UserManager):
    def get_queryset(self):
        return User.objects.filter(groups__name="API Users")


class APIUser(User):
    """
    These are API specific users -- they get no access to the django admin
    console, and they have API tokens.
    """

    objects = APIUserManager()

    def clean(self):
        if not self.username.startswith("api-"):
            self.username = "api-" + self.username

    class Meta:
        proxy = True
        verbose_name = "API User"
        verbose_name_plural = "API Users"


@receiver(post_save, sender=APIUser)
def finalize_api_user(sender: Type[Model], instance: Model, created: bool, **kwargs):  # noqa: ARG001
    if created:
        g = Group.objects.get(name="API Users")
        g.user_set.add(instance)  # type: ignore[attr-defined]
        Token.objects.get_or_create(user=instance)
