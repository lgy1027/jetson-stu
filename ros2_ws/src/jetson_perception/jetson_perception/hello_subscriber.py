import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HelloSubscriber(Node):
    def __init__(self) -> None:
        super().__init__("hello_subscriber")
        self.message_count = 0
        self.subscription = self.create_subscription(
            String,
            "/course/hello",
            self.receive_message,
            10,
        )

    def receive_message(self, message: String) -> None:
        self.message_count += 1
        self.get_logger().info(f"收到第 {self.message_count} 条: {message.data}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = HelloSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
