import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'summer_task_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include all launch files
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yashvant',
    maintainer_email='yashvant280607@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'collision_avoidance_node = summer_task_pkg.collision_avoidance_node:main',
            'circle_patrol_server = summer_task_pkg.circle_patrol_server:main',
            'circle_patrol_client = summer_task_pkg.circle_patrol_client:main'
        ],
    },
)
