import os

from setuptools import setup, find_packages

melogger_path = os.path.abspath(os.path.dirname(__file__))

VERSION = "1.0.1"
DESCRIPTION = "A custom plug and play logger"

setup(
    name=f"melogger",
    url="https://github.com/mihaiep/melogger",
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README.md', 'r').read(),
    author="Mihai Eduard Petcu",
    packages=find_packages(exclude="tests"),
    license="GNU GENERAL PUBLIC LICENSE",
    keywords=["log", "logger", "easy logger", "custom logger"],
    platforms=["Windows", "Linux", "MacOS", "MacOS X", "Unix"],
)
