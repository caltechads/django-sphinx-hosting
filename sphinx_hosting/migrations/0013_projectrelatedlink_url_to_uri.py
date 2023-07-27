# Generated by Django 4.2.3 on 2023-07-27 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sphinxhostingcore', '0012_project_relatedlinks'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectrelatedlink',
            old_name='url',
            new_name='uri',
        ),
        migrations.AlterUniqueTogether(
            name='projectrelatedlink',
            unique_together={('project', 'uri')},
        ),
    ]
