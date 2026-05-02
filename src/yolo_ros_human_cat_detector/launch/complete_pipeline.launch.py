from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    # Camera parameters
    device = LaunchConfiguration('device')
    camera_topic = LaunchConfiguration('camera_topic')
    
    # Detector parameters
    model = LaunchConfiguration('model')
    confidence = LaunchConfiguration('confidence')
    device_compute = LaunchConfiguration('device_compute')
    annotated_image_topic = LaunchConfiguration('annotated_image_topic')
    detections_topic = LaunchConfiguration('detections_topic')

    return LaunchDescription(
        [
            # Camera launch arguments
            DeclareLaunchArgument('device', default_value='/dev/video2'),
            DeclareLaunchArgument('camera_topic', default_value='/camera/image_raw'),
            
            # Detector launch arguments
            DeclareLaunchArgument('model', default_value='yolov8n.pt'),
            DeclareLaunchArgument('confidence', default_value='0.35'),
            DeclareLaunchArgument('device_compute', default_value='cpu'),
            DeclareLaunchArgument('annotated_image_topic', default_value='/yolo/annotated_image'),
            DeclareLaunchArgument('detections_topic', default_value='/yolo/detections_json'),
            
            # Camera node
            Node(
                package='yolo_ros_human_cat_detector',
                executable='webcam_publisher_node',
                name='camera_node',
                output='screen',
                parameters=[
                    {
                        'device': device,
                        'image_topic': camera_topic,
                        'frame_id': 'c310_camera',
                        'width': 1280,
                        'height': 720,
                        'fps': 15.0,
                        'backend': 'v4l2',
                    }
                ],
            ),
            
            # Detector node
            Node(
                package='yolo_ros_human_cat_detector',
                executable='yolo_detector_node',
                name='detector_node',
                output='screen',
                parameters=[
                    {
                        'input_topic': camera_topic,
                        'output_image_topic': annotated_image_topic,
                        'output_detections_topic': detections_topic,
                        'model': model,
                        'confidence': confidence,
                        'device': device_compute,
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
