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

**Detections**

The detector publishes structured detections on `/yolo/detections` with type `vision_msgs/Detection2DArray` and an annotated image on `/yolo/annotated_image` (`sensor_msgs/Image`). Each `Detection2D` includes a `results` entry with `hypothesis.class_id` (string) and `hypothesis.score`, and a `bbox` with `center.position.x/y` and `size_x/size_y`.

Minimal Python subscriber example:

```python
from vision_msgs.msg import Detection2DArray

def cb(msg: Detection2DArray):
	for det in msg.detections:
		cls = det.results[0].hypothesis.class_id
		score = det.results[0].hypothesis.score
		cx = det.bbox.center.position.x
		cy = det.bbox.center.position.y
		print(cls, score, cx, cy)
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