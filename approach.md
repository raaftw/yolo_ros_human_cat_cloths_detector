# Approach

The assignment was open-ended so I picked detection classes that were relevant to something I actually wanted to build: a node that could run on my own mobile robot and detect people, cats, and clothes on the floor. I used a Logitech C310 webcam I already had.

My approach was to build incrementally and test each step before moving on. Camera publisher on the laptop first, then the YOLO detection node, then porting the camera node to the Raspberry Pi. The idea is simple — if steps 1–3 work and step 4 breaks, the bug is in step 4. It made debugging a lot easier.

I picked YOLOv8n because it's fast enough for real-time inference and pretrained on COCO which already covers person and cat. For ROS 2 I used standard message types — raw image for the stream and Detection2DArray for bounding boxes — keeping it compatible with other nodes out of the box.

What worked well was the step-by-step approach, the full pipeline runs and publishes detections correctly. What I didn't finish was clothing detection — it's not a COCO class so it would need fine-tuning on a custom dataset, which I ran out of time for.
