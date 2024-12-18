import os  # noqa: INP001
import sys
from typing import Dict, List, Optional, Tuple  # noqa: UP035

import sphinx_rtd_theme  # pylint: disable=unused-import  # noqa:F401

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
sys.path.insert(0, os.path.abspath("../../sandbox"))  # noqa: PTH100

# -- Project information -----------------------------------------------------

# the master toctree document
master_doc: str = "index"

project: str = "django-sphinx-hosting"
copyright: str = "2022, Caltech IMSS ADS"  # noqa: A001
author: str = "Caltech IMSS ADS"

# The full version, including alpha/beta/rc tags
release: str = "1.6.1"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions: List[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme",
    "sphinxcontrib_django",
    "sphinxcontrib.openapi",
]

source_suffix: str = ".rst"

# Add any paths that contain templates here, relative to this directory.
templates_path: List[str] = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: List[str] = ["_build"]

add_function_parentheses: bool = False
add_module_names: bool = True


autodoc_member_order: str = "groupwise"

# Make Sphinx not expand all our Type Aliases
autodoc_type_aliases: Dict[str, str] = {}

# the locations and names of other projects that should be linked to this one
intersphinx_mapping: Dict[str, Tuple[str, Optional[str]]] = {  # noqa: FA100
    "python": ("https://docs.python.org/3", None),
    "django": (
        "http://docs.djangoproject.com/en/dev/",
        "http://docs.djangoproject.com/en/dev/_objects/",
    ),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}

# Configure the path to the Django settings module
django_settings: str = "demo.settings"
# Include the database table names of Django models
django_show_db_tables: bool = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme: str = "sphinx_rtd_theme"
html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = True
