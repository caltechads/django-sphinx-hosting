# Generated by Django 5.0.7 on 2024-07-10 22:13

from django.db import migrations


def set_latest_version(apps, schema_editor):
    """
    Set the :py:attr:`sphinx_hosting.models.Project.latest_version` field for all
    projects to the latest version using the same logic as the @property
    latest_version in :py:class:`sphinx_hosting.models.Project` for versions < 1.4.2
    """
    Project = apps.get_model("sphinxhostingcore", "Project")
    for project in Project.objects.all():
        latest_version = project.versions.order_by('-modified').first()
        project.latest_version = latest_version
        project.save()


def unset_latest_version(apps, schema_editor):
    """
    Set the :py:attr:`sphinx_hosting.models.Project.latest_version` field to
    None for all projects.   We're undoing the work of the ``set_latest_version
    function``.
    """
    Project = apps.get_model("sphinxhostingcore", "Project")
    for project in Project.objects.all():
        project.latest_version = None
        project.save()


class Migration(migrations.Migration):

    dependencies = [
        ('sphinxhostingcore', '0014_latest_version_as_field'),
    ]

    operations = [
        migrations.RunPython(set_latest_version, reverse_code=unset_latest_version),
    ]
