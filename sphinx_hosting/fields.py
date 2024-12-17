from typing import List  # noqa: UP035

from django.core.validators import RegexValidator
from django.db import models

from sphinx_hosting import form_fields

from .validators import validate_machine_name


class MachineNameField(models.SlugField):
    """
    A :py:class:`django.forms.SlugField` that also allows "." characters.  "."
    is not uncommon in some project names, especially if the project is named
    after the website domain it hosts.
    """

    default_validators: List[RegexValidator] = [validate_machine_name]  # noqa: RUF012

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": form_fields.MachineNameField,
                "allow_unicode": self.allow_unicode,
                **kwargs,
            }
        )
