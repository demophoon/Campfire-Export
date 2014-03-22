#!/usr/bin/env python
from setuptools import setup

setup(
    name="Campfire Export",
    version="0.0.1",
    author="Britt Gresham",
    author_email="bgresham@egov.com",
    description=("Exports campfire logs to a database"),
    license="MIT",
    install_requires=[
        "SQLAlchemy",
        "pinder",
    ],
)
