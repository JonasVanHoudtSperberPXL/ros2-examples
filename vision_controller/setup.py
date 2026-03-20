from setuptools import find_packages, setup

package_name = 'vision_controller'

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
            'drive = vision_controller.drive:main',
            'process_front_camera = vision_controller.process_front_camera:main',
            'process_images = vision_controller.process_images:main'
        ],
    },
)
