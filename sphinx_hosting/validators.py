from typing import Any

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.html import strip_tags


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
