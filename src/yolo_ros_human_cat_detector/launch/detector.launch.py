from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    input_topic = LaunchConfiguration('input_topic')
    output_image_topic = LaunchConfiguration('output_image_topic')
    output_detections_topic = LaunchConfiguration('output_detections_topic')
    model = LaunchConfiguration('model')
    confidence = LaunchConfiguration('confidence')
    device = LaunchConfiguration('device')

    return LaunchDescription(
        [
            DeclareLaunchArgument('input_topic', default_value='/camera/image_raw'),
            DeclareLaunchArgument('output_image_topic', default_value='/yolo/annotated_image'),
            DeclareLaunchArgument('output_detections_topic', default_value='/yolo/detections_json'),
            DeclareLaunchArgument('model', default_value='yolov8n.pt'),
            DeclareLaunchArgument('confidence', default_value='0.35'),
            DeclareLaunchArgument('device', default_value='cpu'),
            Node(
                package='yolo_ros_human_cat_detector',
                executable='yolo_detector_node',
                name='yolo_detector_node',
                output='screen',
                parameters=[
                    {
                        'input_topic': input_topic,
                        'output_image_topic': output_image_topic,
                        'output_detections_topic': output_detections_topic,
                        'model': model,
                        'confidence': confidence,
                        'device': device,
                    }
                ],
            ),
        ]
    )
