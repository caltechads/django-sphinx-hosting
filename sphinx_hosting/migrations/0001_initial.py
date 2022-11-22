# Generated by Django 4.1.2 on 2022-11-18 23:12

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import sphinx_hosting.models
import sphinx_hosting.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(help_text='The human name for this project', max_length=100, verbose_name='Project Name')),
                ('description', models.CharField(blank=True, help_text='A brief description of this project', max_length=256, null=True, validators=[sphinx_hosting.validators.NoHTMLValidator()], verbose_name='Brief Description')),
                ('machine_name', models.SlugField(help_text='Must be unique.  Set this to the value of "project" in Sphinx\'s. conf.py', unique=True, verbose_name='Machine Name')),
            ],
            options={
                'verbose_name': 'project',
                'verbose_name_plural': 'projects',
            },
        ),
        migrations.CreateModel(
            name='SphinxPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('relative_path', models.CharField(help_text='The path to the page under our top slug', max_length=255, verbose_name='Relative page path')),
                ('content', models.TextField(help_text='The full JSON payload for the page', verbose_name='Content')),
                ('title', models.CharField(help_text='Just the title for the page, extracted from the page JSON', max_length=255, verbose_name='Title')),
                ('body', models.TextField(blank=True, help_text='Just the body for the page, extracted from the page JSON. Some pages have no body.', verbose_name='Body')),
                ('local_toc', models.TextField(blank=True, default=None, help_text='Table of Contents for headings in this page', null=True, verbose_name='Local Table of Contents')),
                ('next_page', models.OneToOneField(help_text='The next page in the documentation set', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='previous_page', to='sphinxhostingcore.sphinxpage')),
                ('parent', models.ForeignKey(help_text='The parent page of this page', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='sphinxhostingcore.sphinxpage')),
            ],
            options={
                'verbose_name': 'sphinx page',
                'verbose_name_plural': 'sphinx pages',
            },
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('version', models.CharField(help_text='A version of our project', max_length=64, verbose_name='Version')),
                ('head', models.OneToOneField(help_text='The top page of the documentation set for this version of our project', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='sphinxhostingcore.sphinxpage')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='sphinxhostingcore.project')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='sphinxpage',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='sphinxhostingcore.version'),
        ),
        migrations.CreateModel(
            name='SphinxImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('orig_path', models.CharField(help_text='The original path to this file in the Sphinx documentation package', max_length=256, verbose_name='Original Path')),
                ('file', models.FileField(help_text='The actual image file', upload_to=sphinx_hosting.models.sphinx_image_upload_to, verbose_name='An image file')),
                ('version', models.ForeignKey(help_text='The version of our project documentation with which this image is associated', on_delete=django.db.models.deletion.CASCADE, related_name='images', to='sphinxhostingcore.version')),
            ],
            options={
                'verbose_name': 'sphinx image',
                'verbose_name_plural': 'sphinx images',
                'unique_together': {('version', 'orig_path')},
            },
        ),
    ]
