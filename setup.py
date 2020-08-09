import ast
import codecs
import re
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))


def read(*parts):
    with codecs.open(path.join(here, *parts), 'r') as fp:
        return fp.read()


_version_re = re.compile(r"__version__\s+=\s+(.*)")


def find_version(*where):
    return str(ast.literal_eval(_version_re.search(read(*where)).group(1)))


REQ_BASE = [
    'Falcon',
    'Pony',
    'python-dotenv',
    'psycopg2-binary',
    'requests',
]

REQ_TEST = [
    'pytest',
    'pytest-cov',
]

REQ_DEV = REQ_TEST + [
    'ipdb',
    'wheel',
    'flake8',
    'flake8-builtins',
    'flake8-bugbear',
    'flake8-mutable',
    'flake8-comprehensions',
    'flake8-pytest-style',
    'pep8-naming',
    'dlint',
    'rope',
    'isort',
    'werkzeug[watchdog]',
]


setup(
    name='backend',
    version=find_version('src', 'backend', '__init__.py'),
    author='Jarek Zgoda',
    author_email='jarek.zgoda@gmail.com',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    url='http://github.com/zgoda/paxful-backend',
    install_requires=REQ_BASE,
    tests_require=REQ_TEST,
    extras_require={
        'test': REQ_TEST,
        'dev': REQ_DEV,
    },
    entry_points={
        'console_scripts': [
            'runbackend=backend.cli:serve',
        ],
    },
    python_requires='~=3.7',
)
