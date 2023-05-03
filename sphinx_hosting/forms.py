from typing import Type

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, HTML, ButtonHolder

from crispy_forms.bootstrap import FieldWithButtons
from django import forms
from django.db.models import Model
from django.urls import reverse, reverse_lazy
from haystack.forms import SearchForm

from .models import Project


class GlobalSearchForm(SearchForm):
    """
    This is the search form at the top of the sidebar, underneath the logo.  It is
    a subclass of :py:class:`haystack.forms.SearchForm`, and does a search of our
    haystack backend.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal px-3'
        self.helper.form_method = 'get'
        self.helper.form_show_labels = False
        # This is a reverse_lazy on purpose because the form gets instantiated as
        # the urlpatterns are being made
        self.helper.form_action = reverse_lazy('sphinx_hosting:search')
        self.helper.layout = Layout(
            FieldWithButtons(
                Field('q', css_class='text-dark', placeholder='Search'),
                HTML('<button type="submit" class="btn btn-primary"><span class="bi bi-search"></span></button>')
            )
        )


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
            'classifiers',
            'permission_groups',

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
    :py:class:`.ProjectCreateForm` is that the user cannot change
    :py:attr:`sphinx_hosting.models.Project.machine_name` here, but can in
    :py:class:`ProjectCreateForm`.  ``machine_name`` should not change after the
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


class ProjectReadonlyUpdateForm(forms.ModelForm):
    """
    This is the form we use to on the
    :py:class:`sphinx_hosting.views.ProjectDetailView` to show the viewer the
    project title and description.  The difference between this and
    :py:class:`ProjectUpdateForm` is that all the fields are readonly, and there
    are no submit buttons.  We're doing it this way instead of just rendering a
    non-form widget so that we can ensure that the page looks the same.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['readonly'] = True
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col'
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('title'),
                Field('description'),
            )
        )

    class Meta:
        model: Type[Model] = Project
        fields = (
            'title',
            'description',
        )
        widgets = {
            'description': forms.Textarea(
                attrs={
                    'cols': 50,
                    'rows': 3,
                    'readonly': 'readonly',
                }
            ),
        }


class VersionUploadForm(forms.Form):
    """
    This is the form on :py:class:`sphinx_hosting.views.ProjectDetailView` that
    allows the user to upload a new documentation set.

    Keyword Args:
        project: the project to which this documentation set should be
            associated
    """

    file = forms.FileField(label='')

    def __init__(self, *args, project: Project = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form'
        self.helper.form_method = 'post'
        if project:
            self.helper.form_action = reverse(
                'sphinx_hosting:version--upload', kwargs={'slug': project.machine_name}
            )
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('file'),
            ),
            ButtonHolder(
                Submit('submit', 'Import', css_class='btn btn-primary'),
                css_class='d-flex flex-row justify-content-end button-holder'
            )
        )
