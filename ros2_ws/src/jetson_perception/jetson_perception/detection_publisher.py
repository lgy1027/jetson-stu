import rclpy
from rclpy.node import Node

from jetson_interfaces.msg import Detection2D, Detection2DArray


class DetectionPublisher(Node):
    def __init__(self) -> None:
        super().__init__("detection_publisher")
        self.declare_parameter("frame_id", "camera")
        self.declare_parameter("publish_period", 0.5)
        period = float(self.get_parameter("publish_period").value)
        if period <= 0:
            raise ValueError("publish_period 必须大于 0")
        self.publisher = self.create_publisher(
            Detection2DArray, "/perception/detections", 10
        )
        self.timer = self.create_timer(period, self.publish_detection)

    def publish_detection(self) -> None:
        stamp = self.get_clock().now().to_msg()
        frame_id = str(self.get_parameter("frame_id").value)

        detection = Detection2D()
        detection.header.stamp = stamp
        detection.header.frame_id = frame_id
        detection.label = "demo-object"
        detection.score = 0.87
        detection.x_min, detection.y_min = 70, 45
        detection.x_max, detection.y_max = 285, 205

        message = Detection2DArray()
        message.header.stamp = stamp
        message.header.frame_id = frame_id
        message.source_image = "simulated"
        message.detections = [detection]
        self.publisher.publish(message)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DetectionPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
