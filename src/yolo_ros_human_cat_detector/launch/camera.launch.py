from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    device = LaunchConfiguration('device')
    image_topic = LaunchConfiguration('image_topic')
    frame_id = LaunchConfiguration('frame_id')
    width = LaunchConfiguration('width')
    height = LaunchConfiguration('height')
    fps = LaunchConfiguration('fps')
    backend = LaunchConfiguration('backend')

    return LaunchDescription(
        [
            DeclareLaunchArgument('device', default_value='/dev/video2'),
            DeclareLaunchArgument('image_topic', default_value='/camera/image_raw'),
            DeclareLaunchArgument('frame_id', default_value='c310_camera'),
            DeclareLaunchArgument('width', default_value='640'),
            DeclareLaunchArgument('height', default_value='480'),
            DeclareLaunchArgument('fps', default_value='15.0'),
            DeclareLaunchArgument('backend', default_value='v4l2'),
            Node(
                package='yolo_ros_human_cat_detector',
                executable='webcam_publisher_node',
                name='webcam_publisher_node',
                output='screen',
                parameters=[
                    {
                        'device': device,
                        'image_topic': image_topic,
                        'frame_id': frame_id,
                        'width': width,
                        'height': height,
                        'fps': fps,
                        'backend': backend,
                    }
                ],
            ),
        ]
    )