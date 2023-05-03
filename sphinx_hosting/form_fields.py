from django import forms

from .validators import validate_machine_name


class MachineNameField(forms.SlugField):
    """
    This is a form field for our
    :py:class:`sphinx_hosting.fields.MachineNameField` that applies the
    appropriate validators.
    """
    default_validators = [validate_machine_name]