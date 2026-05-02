from setuptools import find_packages, setup

package_name = 'yolo_ros_human_cat_detector'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', [f'resource/{package_name}']),
        (f'share/{package_name}', ['package.xml']),
        (f'share/{package_name}/launch', ['launch/detector.launch.py', 'launch/camera.launch.py', 'launch/complete_pipeline.launch.py']),
        (f'share/{package_name}/config', ['config/detector.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='raaf',
    maintainer_email='raaf@example.com',
    description='ROS2 YOLO detector scaffold for human and cat detection.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'yolo_detector_node = yolo_ros_human_cat_detector.detector_node:main',
            'webcam_publisher_node = yolo_ros_human_cat_detector.camera_node:main',
        ],
    },
)
