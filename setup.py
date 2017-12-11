"""Setup for astpath, adds astpath console_script."""

from setuptools import setup

setup(
    name='email_crawler',
    packages=['email_crawler'],
    version='0.0.1',
    description='A command-line utility for crawling for emails',
    author='H. Chase Stevens',
    author_email='chase@chasestevens.com',
    url='https://github.com/hchasestevens/email-crawler',
    install_requires={
        'lxml>=4.1.1',
        'requests>=2.18.4',
    },
    entry_points={
        'console_scripts': [
            'find-emails = email_crawler.cli:main',
        ]
    },
)
