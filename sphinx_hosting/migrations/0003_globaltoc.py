# Generated by Django 4.1.2 on 2022-12-08 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sphinxhostingcore', '0002_original_html'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='global_toc',
            field=models.TextField(blank=True, default=True, help_text='The global table of contents for this version, if any.  This is HTML, and will only be present if you had "sphinxcontrib-jsonglobaltoc" installed in your "extensions" in the Sphinx conf.py', null=True, verbose_name='Global Table of Contents'),
        ),
    ]
