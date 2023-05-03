from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.html import strip_tags
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _


@deconstructible
class NoHTMLValidator:
    """
    Verify that field contains no HTML
    """
    message: str = 'Cannot contain any HTML'
    code: str = 'invalid'

    def __call__(self, value: str) -> None:
        if not value == strip_tags(value):
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, NoHTMLValidator)
        )


machine_name_re = _lazy_re_compile(r"^[-a-zA-Z0-9_.]+\Z")
validate_machine_name = RegexValidator(
    machine_name_re,
    # Translators: "letters" means latin letters: a-z and A-Z.
    _("Enter a valid “machine name” consisting of letters, numbers, underscores, hyphens or periods."),
    "invalid",
)
