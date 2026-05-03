from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    # Detector parameters
    input_topic = LaunchConfiguration('input_topic')
    model = LaunchConfiguration('model')
    confidence = LaunchConfiguration('confidence')
    device = LaunchConfiguration('device')
    annotated_image_topic = LaunchConfiguration('annotated_image_topic')
    detections_topic = LaunchConfiguration('detections_topic')

    return LaunchDescription(
        [
            # Detector launch arguments
            DeclareLaunchArgument('input_topic', default_value='/camera/image_raw'),
            DeclareLaunchArgument('model', default_value='yolov8n.pt'),
            DeclareLaunchArgument('confidence', default_value='0.35'),
            DeclareLaunchArgument('device', default_value='cpu'),
            DeclareLaunchArgument('annotated_image_topic', default_value='/yolo/annotated_image'),
            DeclareLaunchArgument('detections_topic', default_value='/yolo/detections'),
            
            # Detector node
            Node(
                package='yolo_ros_human_cat_detector',
                executable='yolo_detector_node',
                name='detector_node',
                output='screen',
                parameters=[
                    {
                        'input_topic': input_topic,
                        'output_image_topic': annotated_image_topic,
                        'output_detections_topic': detections_topic,
                        'model': model,
                        'confidence': confidence,
                        'device': device,
                    }
                ],
            ),
            
            # Image viewer for annotated output
            Node(
                package='image_tools',
                executable='showimage',
                name='image_viewer',
                output='screen',
                remappings=[('image', annotated_image_topic)],
            ),
        ]
    )
