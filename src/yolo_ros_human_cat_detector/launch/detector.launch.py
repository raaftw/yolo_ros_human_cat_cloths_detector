from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    input_image_topic = LaunchConfiguration('input_image_topic')
    output_image_topic = LaunchConfiguration('output_image_topic')
    detections_topic = LaunchConfiguration('detections_topic')
    model_name = LaunchConfiguration('model_name')
    confidence_threshold = LaunchConfiguration('confidence_threshold')
    device = LaunchConfiguration('device')

    return LaunchDescription(
        [
            DeclareLaunchArgument('input_image_topic', default_value='/camera/image_raw'),
            DeclareLaunchArgument('output_image_topic', default_value='/yolo/annotated_image'),
            DeclareLaunchArgument('detections_topic', default_value='/yolo/detections'),
            DeclareLaunchArgument('model_name', default_value='yolov8n.pt'),
            DeclareLaunchArgument('confidence_threshold', default_value='0.35'),
            DeclareLaunchArgument('device', default_value='cpu'),
            Node(
                package='yolo_ros_human_cat_detector',
                executable='yolo_detector_node',
                name='yolo_detector_node',
                output='screen',
                parameters=[
                    {
                        'input_image_topic': input_image_topic,
                        'output_image_topic': output_image_topic,
                        'detections_topic': detections_topic,
                        'model_name': model_name,
                        'confidence_threshold': confidence_threshold,
                        'device': device,
                    }
                ],
            ),
        ]
    )
