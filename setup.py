from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="django-sphinx-hosting",
    version="1.1.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django-braces >= 1.15.0",
        "django-crispy-forms>=1.14.0",
        "django-extensions >= 3.2.1",
        "django-filter >= 22.1",
        "django-haystack >= 3.2.1",
        "django-rest-framework-helpers >= 8.5.0",
        "django-theme-academy >= 0.3.0",
        "django-wildewidgets >= 0.16.7",
        "djangorestframework >= 3.14.0",
        "drf-spectacular >= 0.25.1",
        "crispy-bootstrap5",
        "humanize",
        "lxml >= 4.9.1",
        "cssselect >= 1.2.0",
        "rich"
    ],
    author="Caltech IMSS ADS",
    author_email="imss-ads-staff@caltech.edu",
    url="https://github.com/caltechads/django-sphinx-hosting",
    description="Reusable Django app for hosting Sphinx documentation privately.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['documentation', 'sphinx', 'django'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.11',
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Software Development :: Documentation",
    ],
)
