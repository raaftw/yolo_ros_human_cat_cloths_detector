# YOLO ROS2 Human/Cat Detector

Minimal ROS2 Humble workspace that runs a YOLO detector on a webcam stream. It publishes an annotated image and JSON detections.

**Quick overview**
- Package: `src/yolo_ros_human_cat_detector`
- Camera publisher: `webcam_publisher_node` (defaults to Logitech C310 at `/dev/video2`)
- Detector node: `yolo_detector_node` (YOLOv8 by default)
- Combined launch: `launch/complete_pipeline.launch.py`

**First-time setup**

0. Install Python YOLO support (ultralytics) and download model (recommended in a venv):

```bash
# optional: create and activate a virtualenv
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install ultralytics
# ultralytics will download models (e.g. yolov8n.pt) on first use; to pre-download run:
python -c "from ultralytics import YOLO; Y=YOLO('yolov8n.pt'); Y.model"
```

1. Install system deps:

```bash
sudo apt update
sudo apt install ros-humble-image-tools
```

2. Build the workspace (from repo root):

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

**Run full pipeline (camera + detector + viewer)**

Start everything (camera, detector, viewer):

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch yolo_ros_human_cat_detector complete_pipeline.launch.py
```

**Detections JSON**

The detector publishes detection results as JSON on `/yolo/detections_json` (type `std_msgs/String`). Each message contains a JSON array of detections; each detection is an object with the following fields:

- `class`: string — COCO class name (e.g. "person")
- `confidence`: float — detection confidence (0..1)
- `x_min`, `y_min`, `x_max`, `y_max`: ints — bounding box pixel coordinates
- `width`, `height`: ints — box size in pixels
- `center_x`, `center_y`: ints — center pixel coordinates

Example subscriber snippet (Python):

```python
import json
from std_msgs.msg import String

def cb(msg: String):
	detections = json.loads(msg.data)
	for d in detections:
		print(d['class'], d['confidence'], d['center_x'], d['center_y'])
```


**Raw camera stream (smoke test)**

Start camera publisher only:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch yolo_ros_human_cat_detector camera.launch.py
```

View the raw camera stream (viewer expects RGB input):

```bash
ros2 run image_tools showimage --ros-args -r image:=/camera/image_raw
```

**Detector-only**

```bash
ros2 launch yolo_ros_human_cat_detector detector.launch.py
```

**Camera compatibility**
- The code uses OpenCV `VideoCapture` (V4L2 backend). It is not tied to the C310; any V4L2-compatible USB webcam should work. The camera node defaults to `/dev/video2` — change device via the camera launch arg or node parameter to use another device.

**Notes**
- Models (e.g., `yolov8n.pt`) are large — they are ignored by `.gitignore`. Install `ultralytics` so the model can be downloaded/used:

```bash
pip install ultralytics
```