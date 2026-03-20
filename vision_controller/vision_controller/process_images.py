#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class RobustLaneFollower(Node):
    def __init__(self):
        super().__init__('robust_lane_follower')

        # Parameters
        self.declare_parameter('desired_speed', 3.0)
        self.declare_parameter('Kp', 0.002)
        self.declare_parameter('Kd', 0.001)
        self.declare_parameter('hard_angular', 1.2)

        self.desired_speed = self.get_parameter('desired_speed').value
        self.Kp = self.get_parameter('Kp').value
        self.Kd = self.get_parameter('Kd').value
        self.hard_angular = self.get_parameter('hard_angular').value

        # PID state
        self.prev_error = 0.0
        self.last_angular = 0.0

        # Lane memory
        self.last_left_x = None
        self.last_right_x = None

        # Detection confidence
        self.left_detect_count = 0
        self.right_detect_count = 0
        self.detect_threshold = 3

        self.bridge = CvBridge()
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(Image, '/front_camera', self.image_callback, 10)

        self.get_logger().info("Robust lane follower started.")

    def image_callback(self, msg):
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        lane_center, left_x, right_x, vis = self.detect_lanes(image)

        # --- Confidence tracking ---
        if left_x is not None:
            self.left_detect_count += 1
        else:
            self.left_detect_count = 0

        if right_x is not None:
            self.right_detect_count += 1
        else:
            self.right_detect_count = 0

        left_valid = self.left_detect_count >= self.detect_threshold
        right_valid = self.right_detect_count >= self.detect_threshold

        # --- Control logic ---
        angular = self.last_angular

        if left_valid and right_valid:
            image_center = image.shape[1] / 2
            error = lane_center - image_center
            derivative = error - self.prev_error
            angular = -(self.Kp * error + self.Kd * derivative)
            self.prev_error = error

        elif not left_valid and right_valid:
            angular = self.hard_angular  # turn left

        elif not right_valid and left_valid:
            angular = -self.hard_angular  # turn right

        else:
            # No reliable lanes → continue steering direction
            if self.last_angular > 0:
                angular = self.hard_angular
            elif self.last_angular < 0:
                angular = -self.hard_angular
            else:
                angular = 0.0

        # Smooth steering (prevents jitter)
        alpha = 0.7
        angular = alpha * self.last_angular + (1 - alpha) * angular
        self.last_angular = angular

        # Publish
        cmd = Twist()
        cmd.linear.x = self.desired_speed
        cmd.angular.z = angular
        self.cmd_pub.publish(cmd)

        # Visualization
        cv2.imshow("Lane Detection", vis)
        cv2.waitKey(1)

    def detect_lanes(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        s = hsv[:, :, 1]

        _, mask = cv2.threshold(s, 100, 255, cv2.THRESH_BINARY)

        # ROI (bottom half)
        roi = mask[int(mask.shape[0]/2):, :]
        contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        left_x_list = []
        right_x_list = []
        img_center = roi.shape[1] / 2

        vis = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 300:
                continue

            M = cv2.moments(cnt)
            if M['m00'] == 0:
                continue

            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            if cx < img_center:
                left_x_list.append(cx)
            else:
                right_x_list.append(cx)

            cv2.circle(vis, (cx, cy), 5, (0, 0, 255), -1)

        left_x = np.mean(left_x_list) if left_x_list else None
        right_x = np.mean(right_x_list) if right_x_list else None

        # --- Jump filtering ---
        max_jump = 80

        if left_x is not None and self.last_left_x is not None:
            if abs(left_x - self.last_left_x) > max_jump:
                left_x = None

        if right_x is not None and self.last_right_x is not None:
            if abs(right_x - self.last_right_x) > max_jump:
                right_x = None

        if left_x is not None:
            self.last_left_x = left_x
        if right_x is not None:
            self.last_right_x = right_x

        lane_center = None
        if left_x is not None and right_x is not None:
            lane_center = (left_x + right_x) / 2

        # Draw lines
        if left_x is not None:
            cv2.line(vis, (int(left_x), 0), (int(left_x), roi.shape[0]), (255, 0, 0), 2)
        if right_x is not None:
            cv2.line(vis, (int(right_x), 0), (int(right_x), roi.shape[0]), (0, 0, 255), 2)
        if lane_center is not None:
            cv2.line(vis, (int(lane_center), 0), (int(lane_center), roi.shape[0]), (0, 255, 0), 2)

        return lane_center, left_x, right_x, vis


def main(args=None):
    rclpy.init(args=args)
    node = RobustLaneFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()