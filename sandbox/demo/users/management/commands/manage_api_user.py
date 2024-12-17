from demo.users.models import APIUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help: str = "Create or update an API-Only user"

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            type=str,
            help="The username of the API user to create or update",
        )
        parser.add_argument(
            "--token",
            action="store_true",
            dest="show_token",
            default=False,
            help="If provided, show the API Token",
        )
        parser.add_argument(
            "--first-name",
            dest="first_name",
            default=None,
            help="Optional: the user's first name",
        )
        parser.add_argument(
            "--last-name",
            dest="last_name",
            default=None,
            help="Optional: the user's last name",
        )
        parser.add_argument(
            "--email",
            dest="email",
            default=None,
            help="Optional: the contact email for the user",
        )
        parser.add_argument(
            "--update-only",
            dest="update_only",
            default=False,
            help="Optional: don't create the user if they don't currently exist",
        )

    def handle(self, **options):
        try:
            user = APIUser.objects.get(username=options["username"])
        except ObjectDoesNotExist:
            if options["update_only"] or options["show_token"]:
                print(
                    f"No user with username {options['username']} exists, and you "
                    "passed either --token or --update-only"
                )
                print("Aborting.")
            else:
                username = options["username"]
                if not username.startswith("api-"):
                    print('Prefixing the username with "api-" ...')
                    username = f"api-{username}"
                user = APIUser(
                    username=username,
                    first_name=options["first_name"],
                    last_name=options["last_name"],
                    email=options["email"],
                )
                user.save()
                user.refresh_from_db()
                print(
                    f"Created APIUser object for {user.first_name} {user.last_name} "
                    f"({user.username}): ID={user.id}"
                )
                print(f"Token for {user.username}: {user.auth_token.key}")
        else:
            if options["show_token"]:
                print(f"Token for {user.username}: {user.auth_token.key}")
            else:
                updates = {
                    key: value
                    for key, value in options.items()
                    if value is not None
                    and key
                    in [
                        "first_name",
                        "last_name",
                        "email",
                    ]
                }
                if updates:
                    APIUser.objects.filter(pk=user.id).update(**updates)
                print(
                    f"Updated APIUser object for {user.first_name} {user.last_name} "
                    f"({user.username}): ID={user.id}"
                )
