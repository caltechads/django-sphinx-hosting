from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="django-sphinx-hosting",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django-braces >= 1.15.0",
        "django-theme-academy >= 0.1.0",
        "django-wildewidgets >= 0.13.50",
        "django-extensions >= 3.2.1",
        "django-crispy-forms==1.14.0",
        "crispy-bootstrap5",
        "lxml >= 4.9.1",
        "cssselect >= 1.2.0"
    ],
    author="Caltech IMSS ADS",
    author_email="cmalek@caltech.edu",
    url="https://github.com/caltechads/django-sphinx-hosting",
    description="Reusable Django app for hosting Sphinx documentation privately.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['documentation', 'sphinx', 'django'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
)
