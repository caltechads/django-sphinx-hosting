# Generated by Django 4.1.2 on 2023-01-06 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sphinxhostingcore', '0004_next_page_FK'),
    ]

    operations = [
        migrations.AddField(
            model_name='sphinxpage',
            name='orig_global_toc',
            field=models.TextField(blank=True, default=None, help_text='The original global table of contents HTML attached to this page, if any.  This will only be present if you had "sphinxcontrib-jsonglobaltoc" installed in your "extensions" in the Sphinx conf.py', null=True, verbose_name='Global Table of Contents (original)'),
        ),
    ]
