from demo.users.models import APIUser
from django.core.management.base import BaseCommand
from tabulate import tabulate


class Command(BaseCommand):
    help: str = "List API-Only users"

    def handle(self, **options):  # noqa: ARG002
        users = APIUser.objects.all().order_by("username")
        table = []
        for user in users:
            table.append(  # noqa: PERF401
                [
                    user.username,
                    f"{user.first_name} {user.last_name}",
                    user.email,
                    user.auth_token.key,
                    user.date_joined.strftime("%Y-%m-%d"),
                ]
            )
        print(
            tabulate(
                table,
                headers=[
                    "Username",
                    "Full name",
                    "Contact email",
                    "Auth Token",
                    "Created",
                ],
            )
        )
