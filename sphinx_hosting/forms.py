from typing import Type

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, ButtonHolder

from django import forms
from django.db.models import Model
from django.urls import reverse

from .models import Project


class ProjectCreateForm(forms.ModelForm):
    """
    This is the form we use to create a new
    :py:class:`sphinx_hosting.models.Project`.  The difference between this and
    :py:class:`sphinx_hosting.forms.ProjectUpdateForm` is that the user can set
    :py:attr:`sphinx_hosting.models.Project.machine_name` here, but can't in
    :py:class:`sphinx_hosting.forms.ProjectUpdateForm`.  ``machine_name`` should not change after the
    project is created.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('sphinx_hosting:project--create')
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('title'),
                Field('machine_name'),
                Field('description'),
            ),
            ButtonHolder(
                Submit('submit', 'Save', css_class='btn btn-primary'),
                css_class='d-flex flex-row justify-content-end button-holder'
            )
        )

    class Meta:
        model: Type[Model] = Project
        exclude = (
            # These are relational fields that will be handled separately
            'versions',

            # These are maintained automatically
            'created',
            'modified'
        )
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }


class ProjectUpdateForm(forms.ModelForm):
    """
    This is the form we use to update an existing
    :py:class:`sphinx_hosting.models.Project`.  The difference between this and
    :py:class:`sphinx_hosting.forms.ProjectCreateForm` is that the user cannot change
    :py:attr:`sphinx_hosting.models.Project.machine_name` here, but can in
    :py:class:`sphinx_hosting.forms.ProjectCreateForm`.  ``machine_name`` should not change after the
    project is created.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('sphinx_hosting:project--update', args=[self.instance.machine_name])
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('title'),
                Field('description'),
            ),
            ButtonHolder(
                Submit('submit', 'Save', css_class='btn btn-primary'),
                css_class='d-flex flex-row justify-content-end button-holder'
            )
        )

    class Meta:
        model: Type[Model] = Project
        fields = (
            'title',
            'description',
        )
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 3}),
        }
