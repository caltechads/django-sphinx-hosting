from typing import Type

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, ButtonHolder

from django import forms
from django.db.models import Model
from django.urls import reverse

from .models import Project


class ProjectCreateForm(forms.ModelForm):

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('sphinx_hosting:project--update', args=[self.instance.pk])
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
