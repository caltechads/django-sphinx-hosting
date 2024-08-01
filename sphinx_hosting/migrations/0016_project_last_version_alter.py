# Generated by Django 5.0.7 on 2024-08-01 16:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sphinxhostingcore', '0015_migrate_to_latest_version_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='latest_version',
            field=models.ForeignKey(blank=True, help_text='The latest version of this project.  This is the version that will be shown when you click "Read Docs" on the project page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='sphinxhostingcore.version'),
        ),
    ]