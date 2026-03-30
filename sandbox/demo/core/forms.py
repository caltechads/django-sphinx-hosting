from __future__ import annotations

from typing import TYPE_CHECKING, Final, cast

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Fieldset, Layout, Submit
from django import forms

from sphinx_hosting.models import Classifier, Project

from .models import SearchNote

if TYPE_CHECKING:
    from django.db.models import Model
    from django.forms import Widget


class SearchNoteForm(forms.ModelForm):
    """
    Form used to create and update demo ``SearchNote`` records.

    Keyword Args:
        form_action: URL that should receive the POST submission.

    """

    def __init__(self, *args, form_action: str, **kwargs):
        """
        Configure crispy layout and sorted relation choices for the form.

        Args:
            *args: Positional arguments forwarded to ``ModelForm``.

        Keyword Args:
            form_action: URL that should receive the POST submission.
            **kwargs: Keyword arguments forwarded to ``ModelForm``.

        """
        super().__init__(*args, **kwargs)
        cast(
            "forms.ModelChoiceField", self.fields["project"]
        ).queryset = Project.objects.order_by("title")
        cast(
            "forms.ModelMultipleChoiceField", self.fields["classifiers"]
        ).queryset = Classifier.objects.order_by("name")
        #: Crispy helper used to render the demo note form consistently.
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-lg-3"
        self.helper.field_class = "col"
        self.helper.form_method = "post"
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Fieldset(
                "",
                Field("title"),
                Field("project"),
                Field("classifiers"),
                Field("body"),
            ),
            ButtonHolder(
                Submit("submit", "Save", css_class="btn btn-primary"),
                css_class="d-flex flex-row justify-content-end button-holder",
            ),
        )

    class Meta:
        model: type[Model] = SearchNote
        fields: Final[tuple[str, ...]] = ("title", "project", "classifiers", "body")
        widgets: Final[dict[str, Widget]] = {
            "body": forms.Textarea(attrs={"cols": 50, "rows": 8}),
            "classifiers": forms.SelectMultiple(attrs={"size": 6}),
        }
