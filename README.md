## How to run:

Copy both folders into your ros2_workspace/src directory and run

```
colcon build
source install/setup.bash
```

### Vision_controller:

run 
```
gz sim
```
And open the Prius on Sonoma Raceway map

In seperate terminal windows run:

```
ros2 run ros_gz_bridge parameter_bridge /front_camera@sensor_msgs/msg/Image@gz.msgs.Image
```
```
ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```
```
ros2 run vision_controller process_images
```


### Lidar_controller:

run 
```
gz sim
```
And open the Tugbot in Warehouse map

In seperate terminal windows run:
```
ros2 run ros_gz_bridge parameter_bridge world/world_demo/model/tugbot/link/scan_omni/sensor/scan_omni/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan
```
```
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link tugbot/scan_omni/scan_omni
```
```
ros2 run ros_gz_bridge parameter_bridge /model/tugbot/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```
```
ros2 run lidar_controller marker
```
```
ros2 run lidar_controller driver
```
```
rviz2
```

Change Fixed Frame to base_link
<img width="349" height="198" alt="image" src="https://github.com/user-attachments/assets/083709f4-5b5d-448d-850e-5a15e835ced6" />

Click on Add > By Topic > /robot_marker > Marker > Ok

Click on Add > By Topic > /world > /world_demo > /model > /tugbot > /link > /scan_omni > /sensor > /scan_omni > /scan > LaserScan > Ok

<img width="475" height="331" alt="image" src="https://github.com/user-attachments/assets/6dcd7aa8-627c-4ace-9035-9d303436979b" />

Optionally disable the Grid and change LaserScan > Size (m) to 0.05


### If these don't work, go ask ChatGPT
