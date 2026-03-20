from setuptools import find_packages, setup

package_name = 'lidar_controller'

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
    maintainer='kasm_user',
    maintainer_email='kasm_user@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'listener = lidar_controller.listener:main',
            'visualizer = lidar_controller.visualizer:main',
            'driver = lidar_controller.driver:main',
            'marker = lidar_controller.marker:main'
        ],
    },
)
