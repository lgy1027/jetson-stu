import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HelloPublisher(Node):
    def __init__(self) -> None:
        super().__init__("hello_publisher")
        # 队列深度 10：订阅端短暂变慢时，可暂存最近 10 条消息。
        self.publisher = self.create_publisher(String, "/course/hello", 10)
        self.counter = 0
        # 0.5 秒触发一次回调，也就是约 2 Hz。
        self.timer = self.create_timer(0.5, self.publish_message)

    def publish_message(self) -> None:
        message = String()
        message.data = f"hello from Jetson: {self.counter}"
        self.publisher.publish(message)
        self.get_logger().info(f"发布: {message.data}")
        self.counter += 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = HelloPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
