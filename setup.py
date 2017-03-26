from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='friskby-controlpanel',
    version='0.3',
    description='Friskby device control panel',
    long_description=long_description,
    url='https://github.com/FriskByBergen/python-friskby-controlpanel',
    author='FriskBy Bergen',
    author_email='jonas@drange.net',
    license='GNU General Public License, Version 3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='friskby bergen frisk by rpiparticle a-small-code',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=['friskby', 'flask'],
    extras_require={
        'test': ['coverage'],
    },
)
