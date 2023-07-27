# Generated by Django 4.2.3 on 2023-07-26 18:06

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sphinxhostingcore', '0011_machinenamefield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sphinxpage',
            name='body',
            field=models.TextField(blank=True, help_text='The body for the page, extracted from the page JSON, and modified to suit us.  Some pages have no body.  The body is actually stored as a Django template.', verbose_name='Body'),
        ),
        migrations.CreateModel(
            name='ProjectRelatedLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(help_text='The title for this link', max_length=100, verbose_name='Link Title')),
                ('url', models.URLField(help_text='The URL for this link', max_length=256, verbose_name='Link URL')),
                ('project', models.ForeignKey(help_text='The project to which this link is related', on_delete=django.db.models.deletion.CASCADE, related_name='related_links', to='sphinxhostingcore.project')),
            ],
            options={
                'verbose_name': 'project related link',
                'verbose_name_plural': 'project related links',
                'ordering': ('title',),
                'unique_together': {('project', 'url')},
            },
        ),
    ]
