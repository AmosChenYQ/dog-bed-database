'''Minimal setup.py file'''

from setuptools import setup, find_packages

setup(
    name='dbdb',
    version='0.1',
		author="AmosChenYQ",
    packages=['dbdb'],
    install_requires=[
        'flask',
    ]
)
