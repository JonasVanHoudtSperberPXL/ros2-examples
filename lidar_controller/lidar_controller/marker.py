#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

class RobotMarkerWithHeading(Node):
    def __init__(self):
        super().__init__('robot_marker_with_heading')
        self.pub = self.create_publisher(Marker, '/robot_marker', 10)
        self.timer = self.create_timer(0.1, self.publish_markers)  # 10 Hz

    def publish_markers(self):
        # --- Circle for robot body ---
        body = Marker()
        body.header.frame_id = "base_link"
        body.header.stamp = self.get_clock().now().to_msg()
        body.ns = "robot_body"
        body.id = 0
        body.type = Marker.CYLINDER
        body.action = Marker.ADD
        body.pose.position.x = 0.0
        body.pose.position.y = 0.0
        body.pose.position.z = 0.05  # slightly above ground
        body.pose.orientation.w = 1.0
        body.scale.x = 0.2  # diameter
        body.scale.y = 0.2
        body.scale.z = 0.1  # height
        body.color.r = 0.0
        body.color.g = 1.0
        body.color.b = 0.0
        body.color.a = 1.0

        # --- Arrow for heading ---
        arrow = Marker()
        arrow.header.frame_id = "base_link"
        arrow.header.stamp = self.get_clock().now().to_msg()
        arrow.ns = "robot_heading"
        arrow.id = 1
        arrow.type = Marker.ARROW
        arrow.action = Marker.ADD
        start = Point()
        start.x = 0.0
        start.y = 0.0
        start.z = 0.1  # above circle
        end = Point()
        end.x = 0.3  # forward direction
        end.y = 0.0
        end.z = 0.1
        arrow.points.append(start)
        arrow.points.append(end)
        arrow.scale.x = 0.05  # shaft diameter
        arrow.scale.y = 0.1   # head diameter
        arrow.scale.z = 0.1   # head length
        arrow.color.r = 0.0
        arrow.color.g = 1.0
        arrow.color.b = 0.0
        arrow.color.a = 1.0

        # Publish both markers
        self.pub.publish(body)
        self.pub.publish(arrow)

def main(args=None):
    rclpy.init(args=args)
    node = RobotMarkerWithHeading()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()