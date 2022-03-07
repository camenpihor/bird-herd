"""Package setup."""
import json
from setuptools import find_packages, setup

VERSION_FILE = "../package.json"
REQUIREMENTS_FILE = "requirements.txt"
REQUIREMENTS_DEV_FILE = "requirements-dev.in"

NAME = "bird-herd-api"
DESCRIPTION = "Backend API serving the birding quiz"
AUTHOR = "Camen Piho"
AUTHOR_EMAIL = "camen.piho.r@gmail.com.com"
URL = "https://github.com/camenpihor/bird-herd"


def get_version():
    """Get version."""
    with open(VERSION_FILE) as buffer:
        return json.load(buffer)["version"]


def get_requirements(path):
    """Read requirements file."""
    with open(path) as buffer:
        return buffer.read().splitlines()


setup(
    name=NAME,
    version=get_version(),
    python_requires="~=3.9",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(),
    include_package_data=True,
    description=DESCRIPTION,
    install_requires=get_requirements(REQUIREMENTS_FILE),
    tests_require=get_requirements(REQUIREMENTS_DEV_FILE),
)
