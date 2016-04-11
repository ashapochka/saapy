# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# TODO: by default should be README.rst, will .md work?
with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    saapy_license = f.read()

setup(
    name='saapy',
    version='0.0.1',
    description='SAApy - System Architecture Assessment Toolset',
    long_description=readme,
    author='Andriy Shapochka',
    author_email='ashapochka@gmail.com',
    url='https://github.com/ashapochka/saapy',
    license=saapy_license,
    packages=find_packages(exclude=('tests', 'docs'))
)

# TODO: enhance packaging and add to PYPI,
# ref https://github.com/pypa/sampleproject
