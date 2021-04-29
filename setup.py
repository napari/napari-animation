#!/usr/bin/env python
from setuptools import setup

# https://github.com/pypa/setuptools_scm

setup(
    use_scm_version={"write_to": "napari_animation/_version.py"},
    setup_requires=["setuptools_scm"],
)
