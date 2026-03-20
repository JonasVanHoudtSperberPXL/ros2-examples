import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import threading
import time
from geometry_msgs.msg import Twist


class ImageProcessor(threading.Thread):
    """Separate thread for heavy OpenCV processing."""
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.cv_image = None
        self.running = True
        self.lock = threading.Lock()

    def set_image(self, cv_image):
        """Safely set a new image for processing."""
        with self.lock:
            self.cv_image = cv_image.copy()

    def run(self):
        """Continuously process images in a separate thread."""
        while self.running:
            if self.cv_image is not None:
                with self.lock:
                    img_copy = self.cv_image.copy()

                processed_image = self.process_image(img_copy)
                #self.display_image(processed_image)

            time.sleep(0.03)  # Prevent CPU overuse

    def process_image(self, cv_image):
        height, width, _ = cv_image.shape

        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        _, s, _ = cv2.split(hsv)  # Saturation channel

        # Threshold saturation to isolate track lines
        _, mask = cv2.threshold(s, 80, 255, cv2.THRESH_BINARY)  # tune threshold 50-120

        # ROI: bottom half
        roi_mask = np.zeros_like(mask)
        polygon = np.array([[
            (0, height),
            (width, height),
            (width, int(height * 0.5)),
            (0, int(height * 0.5))
        ]], np.int32)
        cv2.fillPoly(roi_mask, polygon, 255)

        roi = cv2.bitwise_and(mask, roi_mask)

        cv2.imshow("saturation_mask", roi)
            # Histogram across the bottom ROI
        histogram = np.sum(roi, axis=0)

        midpoint = int(histogram.shape[0] / 2)
        leftx = np.argmax(histogram[:midpoint])
        rightx = np.argmax(histogram[midpoint:]) + midpoint

        lane_center = (leftx + rightx) / 2
        image_center = width / 2
        error = lane_center - image_center

        # Create Twist command
        twist = Twist()
        twist.linear.x = 5.0  # forward speed
        twist.angular.z = -error / 400  # proportional steering

        # Publish command
        self.node.cmd_pub.publish(twist)

        # Visualization: show lane center vs image center
        cv2.line(cv_image, (int(lane_center), height-50), (int(lane_center), height), (0,255,0), 3)
        cv2.line(cv_image, (int(image_center), height-50), (int(image_center), height), (0,0,255), 2)

        cv2.imshow("camera_with_lane", cv_image)
        cv2.waitKey(1)

        return cv_image

    def display_image(self, cv_image):
        """Display processed image using OpenCV."""
        cv2.imshow("Processed Image", cv_image)
        cv2.waitKey(0.5)  # Required for OpenCV to update window


class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('image_subscriber')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.subscription = self.create_subscription(
            Image,
            '/front_camera',  # Change if using a different topic
            self.image_callback,
            10
        )
        self.br = CvBridge()
        self.processor = ImageProcessor(self)

    def image_callback(self, msg):
        """Converts ROS 2 Image message to OpenCV format and updates processing thread."""
        try:
            cv_image = self.br.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            self.processor.set_image(cv_image)  # Send image to processing thread
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")


def main():
    rclpy.init()

    node = ImageSubscriber()
    node.processor.start()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("Shutting down")

    finally:
        node.processor.running = False
        node.processor.join()
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
