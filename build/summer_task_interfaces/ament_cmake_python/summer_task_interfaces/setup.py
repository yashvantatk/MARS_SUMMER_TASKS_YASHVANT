from setuptools import find_packages
from setuptools import setup

setup(
    name='summer_task_interfaces',
    version='0.0.0',
    packages=find_packages(
        include=('summer_task_interfaces', 'summer_task_interfaces.*')),
)
