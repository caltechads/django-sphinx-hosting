from django import forms

from .validators import validate_machine_name


class MachineNameField(forms.SlugField):
    """
    This is a form field for our
    :py:class:`sphinx_hosting.fields.MachineNameField` that applies the
    appropriate validators.

    The difference this field and :py:class:`django.forms.SlugField` is that
    this field will allow "-" characters in the value
    """
    default_validators = [validate_machine_name]
