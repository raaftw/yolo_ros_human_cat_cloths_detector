from __future__ import annotations

from dataclasses import dataclass
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


@dataclass
class DetectorConfig:
    input_image_topic: str
    output_image_topic: str
    detections_topic: str
    model_name: str
    confidence_threshold: float
    device: str
    publish_annotated_image: bool


class YoloDetectorNode(Node):
    """Starter ROS2 node for a YOLO-based detector.

    This scaffold wires the ROS2 interfaces so you can plug in a model next.
    """

    def __init__(self) -> None:
        super().__init__('yolo_detector_node')

        self.declare_parameter('input_image_topic', '/camera/image_raw')
        self.declare_parameter('output_image_topic', '/yolo/annotated_image')
        self.declare_parameter('detections_topic', '/yolo/detections')
        self.declare_parameter('model_name', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.35)
        self.declare_parameter('device', 'cpu')
        self.declare_parameter('publish_annotated_image', True)

        self.config = DetectorConfig(
            input_image_topic=self.get_parameter('input_image_topic').value,
            output_image_topic=self.get_parameter('output_image_topic').value,
            detections_topic=self.get_parameter('detections_topic').value,
            model_name=self.get_parameter('model_name').value,
            confidence_threshold=float(self.get_parameter('confidence_threshold').value),
            device=self.get_parameter('device').value,
            publish_annotated_image=bool(self.get_parameter('publish_annotated_image').value),
        )

        self.subscription = self.create_subscription(
            Image,
            self.config.input_image_topic,
            self.image_callback,
            10,
        )
        self.subscription  # prevent unused-variable warning in some linters

        self.get_logger().info(
            'YOLO detector scaffold ready. Input: %s, output: %s, detections: %s, model: %s, device: %s'
            % (
                self.config.input_image_topic,
                self.config.output_image_topic,
                self.config.detections_topic,
                self.config.model_name,
                self.config.device,
            )
        )

    def image_callback(self, msg: Image) -> None:
        _ = msg
        self.get_logger().debug('Received an image frame; model inference is not wired yet.')


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = YoloDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
