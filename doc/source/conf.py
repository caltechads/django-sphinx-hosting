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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

from typing import List, Dict, Tuple, Optional
import sphinx_rtd_theme  # pylint: disable=unused-import  # noqa:F401

# -- Project information -----------------------------------------------------

# the master toctree document
master_doc = "index"

project = 'django-sphinx-hosting'
copyright = '2022, Caltech IMSS ADS'  # pylint: disable=redefined-builtin
author = 'Caltech IMSS ADS'

# The full version, including alpha/beta/rc tags
release = '1.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme'
]

source_suffix = ".rst"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: List[str] = ['_build']

add_function_parentheses = False
add_module_names = True

# Make Sphinx not expand all our Type Aliases

autodoc_member_order = 'bysource'
autodoc_type_aliases = {
    'LDAPData': 'ldap_faker.types.LDAPData',
    'CILDAPData': 'ldap_faker.types.CILDAPData',
    'LDAPRecord': 'ldap_faker.types.LDAPRecord',
    'LDAPSearchResult': 'ldap_faker.types.LDAPSearchResult',
    'LDAPSearchDirectory': 'ldap_faker.types.LDAPSearchDirectory',
    'LDAPObjectStore': 'ldap_faker.types.LDAPObjectStore',
    'RawLDAPObjectStore': 'ldap_faker.types.RawLDAPObjectStore',
    'LDAPOptionValue': 'ldap_faker.types.LDAPOptionValue',
    'LDAPOptionStore': 'ldap_faker.types.LDAPOptionStore',
    'ModList': 'ldap_faker.types.ModList',
    'AddModList': 'ldap_faker.types.AddModList',
    'LDAPFixtureList': 'ldap_faker.types.LDAPFixtureList',
}

# the locations and names of other projects that should be linked to this one
intersphinx_mapping: Dict[str, Tuple[str, Optional[str]]] = {
    'python': ('https://docs.python.org/3', None),
    'python-ldap': ('https://www.python-ldap.org/en/latest/', None)

}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = True
