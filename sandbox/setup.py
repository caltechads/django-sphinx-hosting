#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="sphinx_hosting_demo",
    version="0.1.0",
    description="",
    author="Caltech IMSS ADS",
    author_email="imss-ads-staff@caltech.edu",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "htmlcov"])
)
