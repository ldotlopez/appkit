# -*- encoding: utf-8 -*-

from setuptools import setup

from appkit import version
version = '.'.join([str(x) for x in version])

with open("requirements.txt") as fh:
    pkgs = fh.readlines()

pkgs = [x.strip() for x in pkgs]
pkgs = [x for x in pkgs if x and x[0] != '#']

setup(
    name='appkit',
    version=version,
    author='Luis López',
    author_email='ldotlopez@gmail.com',
    packages=[
        'appkit',
        'appkit.application',
        'appkit.blocks',
        'appkit.db'
    ],
    scripts=[],
    url='https://github.com/ldotlopez/appkit',
    license='LICENSE.txt',
    description='Application toolkit',
    long_description=open('README').read(),
    install_requires=pkgs,
)
