from setuptools import setup, find_packages


setup(
    name = 'lorisal',
    version = '0.1',
    author= 'OU Data Lab',
    author_email='daniel.helm@ou.edu',
    packages=find_packages(exclude=('tests', 'docs'))
)

