import pathlib
import re
import subprocess

from setuptools import setup

ROOT = pathlib.Path(__file__).parent

with open(ROOT / 'requirements' / 'pypi.txt', 'r', encoding='utf-8') as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name='discord.gui',
    author='Starwort',
    url='https://github.com/Starwort/discord.gui',

    license='GNU GPL 3',
    description='A discord.py extension providing a GUI interface to monitor the bot and modify command settings',
    project_urls={
        'Code': 'https://github.com/Starwort/discord.gui',
        'Issue tracker': 'https://github.com/Starwort/discord.gui/issues'
    },

    version='1.0',
    packages=['discord_gui'],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    python_requires='>=3.6.0',

    keywords='discord.gui discord.py discord cog gui extension',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU GPL 3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities'
    ]
)
