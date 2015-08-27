  # -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages

__version__ = '1.0.0.gm'

install_requires = [
    'Flask', 
    'pycrypto', 
    'pyyaml', 
    'simplejson', 
    'gevent', 
    'requests', 
    'iso8601',
    'blinker',
    'SQLAlchemy',
    'pymysql',
    'mysql-python',
    'redis',
    'docopt',
    'pillow', # 用于画验证码
]
if sys.version_info < (2, 7):
    install_requires += ['argparse']


setup(
    name = "melee",
    version = __version__,
    packages = find_packages(exclude=["tests.*", "tests"]),
    install_requires = install_requires, 
    license='BSD',
    author='yingmulee',
    author_email='yingmulee@163.com',
    maintainer='yingmulee',
    maintainer_email='yingmulee@163.com',
    description='common web server framework based on Flask',
    long_description=__doc__,
    url='https://github.com/leeyingmu/melee',
    entry_points = {
        'console_scripts': [
            'meleeok = demo:meleeok' 
        ]
    }
)

