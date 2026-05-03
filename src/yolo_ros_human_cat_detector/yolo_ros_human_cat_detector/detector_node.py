#!/usr/bin/env python3
"""YOLO detector node for ROS2 - publishes annotated image and JSON detections."""

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSHistoryPolicy
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from geometry_msgs.msg import Pose2D

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


class YoloDetectorNode(Node):
    """YOLO detector for person and cat detection."""

    def __init__(self) -> None:
        super().__init__('yolo_detector_node')

        if YOLO is None:
            raise ImportError('ultralytics not installed. Install with: pip install ultralytics')

        # Declare parameters
        self.declare_parameter('input_topic', '/camera/image_raw')
        self.declare_parameter('output_image_topic', '/yolo/annotated_image')
        self.declare_parameter('output_detections_topic', '/yolo/detections')
        self.declare_parameter('model', 'yolov8n.pt')
        self.declare_parameter('confidence', 0.35)
        self.declare_parameter('device', 'cpu')

        # Get parameters
        self.input_topic = self.get_parameter('input_topic').value
        self.output_image_topic = self.get_parameter('output_image_topic').value
        self.output_detections_topic = self.get_parameter('output_detections_topic').value
        model_name = self.get_parameter('model').value
        self.confidence = self.get_parameter('confidence').value
        device = self.get_parameter('device').value

        # Load YOLO model
        self.get_logger().info(f'Loading YOLO model: {model_name}')
        self.model = YOLO(model_name)
        self.model.to(device)

        self.bridge = CvBridge()

        # Only publish person and cat detections by default
        self.allowed_classes = {'person', 'cat'}

        # Publishers (depth=1: only keep latest, drop old ones)
        qos_pub = QoSProfile(depth=1, history=QoSHistoryPolicy.KEEP_LAST)
        self.image_pub = self.create_publisher(Image, self.output_image_topic, qos_profile=qos_pub)
        self.detections_pub = self.create_publisher(Detection2DArray, self.output_detections_topic, qos_profile=qos_pub)

        # Subscriber (depth=1: only keep latest image, drop old ones)
        qos = QoSProfile(depth=1, history=QoSHistoryPolicy.KEEP_LAST)
        self.create_subscription(Image, self.input_topic, self.image_callback, qos)

        self.get_logger().info(
            f'YOLO detector ready. Input: {self.input_topic}, '
            f'Image output: {self.output_image_topic}, '
            f'Detections: {self.output_detections_topic}'
        )

    def image_callback(self, msg: Image) -> None:
        """Process incoming image."""
        # Convert ROS Image to OpenCV (BGR)
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Run YOLO inference
        results = self.model(cv_image, conf=self.confidence, verbose=False)

        # Extract detections as Detection2DArray
        detections_msg = self._extract_detections(results, msg.header)

        # Draw bounding boxes and publish annotated image (use YOLO results for boxes)
        annotated = cv_image.copy()
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                class_name = self.model.names.get(class_id, f'class_{class_id}')
                # Skip classes we don't want
                if class_name not in self.allowed_classes:
                    continue

                det = {
                    'class': class_name,
                    'confidence': round(confidence, 3),
                    'x_min': int(x1),
                    'y_min': int(y1),
                    'x_max': int(x2),
                    'y_max': int(y2),
                }
                self._draw_detection(annotated, det)

        # Convert BGR to RGB for proper color display
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        annotated_msg = self.bridge.cv2_to_imgmsg(annotated_rgb, encoding='rgb8')
        annotated_msg.header = msg.header
        self.image_pub.publish(annotated_msg)

        # Publish structured detections
        self.detections_pub.publish(detections_msg)

    def _extract_detections(self, results: list, header) -> Detection2DArray:
        """Convert YOLO results to a vision_msgs/Detection2DArray."""
        detections_msg = Detection2DArray()
        detections_msg.header = header

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x_center = float((x1 + x2) / 2.0)
                y_center = float((y1 + y2) / 2.0)
                width = float(x2 - x1)
                height = float(y2 - y1)

                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                class_name = self.model.names.get(class_id, f'class_{class_id}')

                # Skip classes not in allowed set
                if class_name not in self.allowed_classes:
                    continue

                # Build Detection2D
                det = Detection2D()
                det.header = header

                # Bounding box center (Pose2D) and size
                # set fields on the existing submessage to avoid type assertion issues
                # BoundingBox2D.center uses a Pose2D with a `position` field and `theta`
                det.bbox.center.position.x = float(x_center)
                det.bbox.center.position.y = float(y_center)
                det.bbox.center.theta = 0.0
                det.bbox.size_x = float(width)
                det.bbox.size_y = float(height)

                # Hypothesis: use class name as id
                hyp = ObjectHypothesisWithPose()
                # hypothesis uses `class_id` (int) and `score`
                # `class_id` in ObjectHypothesis is a string identifier
                hyp.hypothesis.class_id = str(class_name)
                hyp.hypothesis.score = float(confidence)
                det.results.append(hyp)

                detections_msg.detections.append(det)

        return detections_msg

    def _draw_detection(self, image: np.ndarray, detection: dict) -> None:
        """Draw a single detection box on image."""
        x1 = detection['x_min']
        y1 = detection['y_min']
        x2 = detection['x_max']
        y2 = detection['y_max']

        # Choose color based on class
        color = (0, 255, 0) if detection['class'] == 'person' else (255, 0, 0)  # Green=person, Blue=cat

        # Draw box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        # Draw label
        label = f"{detection['class']} {detection['confidence']:.2f}"
        cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def main() -> None:
    rclpy.init()
    node = YoloDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.destroy_node()
        except Exception:
            pass
        try:
            rclpy.shutdown()
        except Exception:
            # rclpy may already be shutting down from the launch system
            pass


if __name__ == '__main__':
    main()

