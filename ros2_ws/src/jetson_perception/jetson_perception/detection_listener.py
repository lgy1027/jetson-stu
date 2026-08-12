import rclpy
from rclpy.node import Node

from jetson_interfaces.msg import Detection2DArray


class DetectionListener(Node):
    def __init__(self) -> None:
        super().__init__("detection_listener")
        self.received = 0
        self.subscription = self.create_subscription(
            Detection2DArray,
            "/perception/detections",
            self.receive_detections,
            10,
        )

    def receive_detections(self, message: Detection2DArray) -> None:
        self.received += 1
        labels = ", ".join(item.label for item in message.detections) or "无结果"
        self.get_logger().info(
            f"第 {self.received} 帧 frame={message.header.frame_id} "
            f"source={message.source_image} detections={labels}"
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DetectionListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
