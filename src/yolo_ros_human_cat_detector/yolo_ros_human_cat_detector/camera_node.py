from __future__ import annotations

from dataclasses import dataclass

import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Header


@dataclass
class CameraConfig:
    device: str
    image_topic: str
    frame_id: str
    width: int
    height: int
    fps: float
    backend: str


class WebcamPublisherNode(Node):
    """Publish frames from the Logitech C310 as ROS2 Image messages."""

    def __init__(self) -> None:
        super().__init__('webcam_publisher_node')

        self.declare_parameter('device', '/dev/video2')
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('frame_id', 'c310_camera')
        self.declare_parameter('width', 640)
        self.declare_parameter('height', 480)
        self.declare_parameter('fps', 15.0)
        self.declare_parameter('backend', 'v4l2')

        self.config = CameraConfig(
            device=str(self.get_parameter('device').value),
            image_topic=str(self.get_parameter('image_topic').value),
            frame_id=str(self.get_parameter('frame_id').value),
            width=int(self.get_parameter('width').value),
            height=int(self.get_parameter('height').value),
            fps=float(self.get_parameter('fps').value),
            backend=str(self.get_parameter('backend').value),
        )

        self.publisher = self.create_publisher(Image, self.config.image_topic, 10)
        self.capture = self._open_capture()
        self.timer = self.create_timer(1.0 / self.config.fps, self.publish_frame)

        self.get_logger().info(
            'Webcam publisher ready. device=%s topic=%s frame_id=%s resolution=%dx%d fps=%.1f'
            % (
                self.config.device,
                self.config.image_topic,
                self.config.frame_id,
                self.config.width,
                self.config.height,
                self.config.fps,
            )
        )

    def _open_capture(self) -> cv2.VideoCapture:
        backend = cv2.CAP_V4L2 if self.config.backend.lower() == 'v4l2' else 0
        capture = cv2.VideoCapture(self.config.device, backend)
        if not capture.isOpened():
            raise RuntimeError(f'Could not open webcam device: {self.config.device}')

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, float(self.config.width))
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self.config.height))
        capture.set(cv2.CAP_PROP_FPS, float(self.config.fps))
        return capture

    def publish_frame(self) -> None:
        success, frame = self.capture.read()
        if not success:
            self.get_logger().warning('Failed to read frame from %s', self.config.device)
            return

        frame = cv2.resize(frame, (self.config.width, self.config.height))
        height, width, channels = frame.shape

        message = Image()
        message.header = Header()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = self.config.frame_id
        message.height = height
        message.width = width
        message.encoding = 'bgr8'
        message.is_bigendian = 0
        message.step = width * channels
        message.data = frame.tobytes()

        self.publisher.publish(message)

    def destroy_node(self) -> bool:
        if hasattr(self, 'capture') and self.capture is not None:
            self.capture.release()
        return super().destroy_node()


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = WebcamPublisherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()