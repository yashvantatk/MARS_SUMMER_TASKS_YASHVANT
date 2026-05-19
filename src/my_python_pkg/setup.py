from setuptools import find_packages, setup

package_name = 'my_python_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yashvant',
    maintainer_email='yashvant@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'py_pub = my_python_pkg.rover_pub:main',
            'py_sub = my_python_pkg.rover_sub:main',
            'py_service = my_python_pkg.rover_service:main',
            'py_client = my_python_pkg.rover_client:main',
        ],
    },
)
