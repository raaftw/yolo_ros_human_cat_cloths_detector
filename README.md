# YOLO ROS2 Human/Cat Detector

This repository is a ROS2 Humble workspace scaffold for a YOLO-based detector that will first target people and cats from a webcam stream.

## What is in the workspace

- A ROS2 Python package at `src/yolo_ros_human_cat_detector`
- A webcam publisher node for the Logitech C310
- A starter detector node with ROS parameters and a camera subscription
- A launch file for starting the node with command-line overrides
- A default parameter file for the node

## Workspace layout

```text
.
├── README.md
└── src
	└── yolo_ros_human_cat_detector
		├── config
		├── launch
		├── package.xml
		├── resource
		├── setup.py
		└── yolo_ros_human_cat_detector
```

## Build and run

### First-time setup after cloning

Install the ROS packages used by the camera node and image viewer:

```bash
sudo apt update
sudo apt install ros-humble-image-tools
```

Then build the workspace from the repository root:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

### Launch the camera publisher

In a new terminal:

```bash
source /opt/ros/humble/setup.bash
cd ~/yolo_ros_human_cat_cloths_detector
source install/setup.bash
ros2 launch yolo_ros_human_cat_detector camera.launch.py
```

To test the camera node by itself on the C310:

```bash
ros2 launch yolo_ros_human_cat_detector camera.launch.py
```

The camera node defaults to `/dev/video2`, which is the Logitech C310 on this laptop.

### View the stream in a terminal app

The image viewer that works reliably here is `showimage` from `image_tools`:

```bash
source /opt/ros/humble/setup.bash
cd ~/yolo_ros_human_cat_cloths_detector
source install/setup.bash
ros2 run image_tools showimage --ros-args -r image:=/camera/image_raw
```

### Optional detector launch

Once the camera view works, you can start the detector node too:

```bash
source /opt/ros/humble/setup.bash
cd ~/yolo_ros_human_cat_cloths_detector
source install/setup.bash
ros2 launch yolo_ros_human_cat_detector detector.launch.py
```

## Next implementation steps

1. Wire in the YOLO model loader and inference path.
2. Publish detections with a structured ROS message.
3. Add annotated image output for visualization.
4. Add a laptop-compute mode and, later, a Pi-only fallback.

## Notes

The current code is a clean scaffold, not a finished detector yet. That keeps the first implementation focused and makes it easier to swap in a pretrained model later.