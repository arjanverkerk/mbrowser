# -*- coding: utf-8 -*-

from setuptools import setup

name = 'mbrowser'
version = '0.1'


setup(
    url='',
    name=name,
    zip_safe=True,
    version=version,
    author='Arjan Verkerk',
    packages=['mbrowser'],
    author_email='arjan.verkerk@gmail.com',
    entry_points={'console_scripts': ['mb=mbrowser.browser:main']},
)
