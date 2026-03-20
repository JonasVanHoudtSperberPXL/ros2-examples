import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np


class WanderBot(Node):
    def __init__(self):
        super().__init__('wander_bot')

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/world/world_demo/model/tugbot/link/scan_omni/sensor/scan_omni/scan',
            self.scan_callback,
            10
        )

        self.cmd_pub = self.create_publisher(Twist, '/model/tugbot/cmd_vel', 10)

        # --- Normal turning ---
        self.turn_direction = 1
        self.turn_timer = 0
        self.turn_duration = 10
        self.threshold = 0.2

        # --- NEW: stuck detection ---
        self.stuck_counter = 0
        self.stuck_threshold = 15  # frames before escape mode

        # --- NEW: escape mode ---
        self.escape_mode = False
        self.escape_timer = 0
        self.escape_duration = 20
        self.escape_direction = 1

    def scan_callback(self, msg):
        ranges = np.array(msg.ranges)

        ranges = np.nan_to_num(ranges, nan=10.0, posinf=10.0, neginf=0.0)

        n = len(ranges)
        front = np.min(ranges[n//3: 2*n//3])
        left = np.min(ranges[2*n//3:])
        right = np.min(ranges[:n//3])

        cmd = Twist()

        # -------------------------
        # ESCAPE MODE (priority)
        # -------------------------
        if self.escape_mode:
            cmd.linear.x = 0.1
            cmd.angular.z = 0.8 * self.escape_direction

            self.escape_timer -= 1
            if self.escape_timer <= 0:
                self.escape_mode = False
                self.stuck_counter = 0

            self.cmd_pub.publish(cmd)
            return

        # -------------------------
        # NORMAL BEHAVIOR
        # -------------------------
        if front > 1.0:
            cmd.linear.x = 0.5
            cmd.angular.z = 0.0

            self.turn_timer = 0
            self.stuck_counter = 0

        else:
            cmd.linear.x = 0.0

            # Increase stuck counter
            self.stuck_counter += 1

            diff = left - right

            if self.turn_timer <= 0:
                if diff > self.threshold:
                    self.turn_direction = 1
                elif diff < -self.threshold:
                    self.turn_direction = -1

                self.turn_timer = self.turn_duration

            cmd.angular.z = 0.5 * self.turn_direction
            self.turn_timer -= 1

            # -------------------------
            # Trigger escape mode
            # -------------------------
            if self.stuck_counter > self.stuck_threshold:
                self.escape_mode = True
                self.escape_timer = self.escape_duration

                # Turn toward more open space
                if left > right:
                    self.escape_direction = 1
                else:
                    self.escape_direction = -1

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = WanderBot()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()