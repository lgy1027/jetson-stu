from pathlib import Path
import json

import cv2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from jetson_interfaces.msg import Detection2D, Detection2DArray


class ImagePerceptionNode(Node):
    def __init__(self) -> None:
        super().__init__("image_perception")
        self.declare_parameter("input_path", "perception/inputs/wide.png")
        self.declare_parameter("output_path", "perception/outputs/ros2/annotated.png")
        self.declare_parameter("frame_id", "camera")
        self.declare_parameter("score_threshold", 0.5)
        self.declare_parameter("publish_period", 1.0)

        period = float(self.get_parameter("publish_period").value)
        threshold = float(self.get_parameter("score_threshold").value)
        if period <= 0:
            raise ValueError("publish_period 必须大于 0")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("score_threshold 必须在 0 到 1 之间")

        self.detection_publisher = self.create_publisher(
            Detection2DArray, "/perception/detections", 10
        )
        self.status_publisher = self.create_publisher(
            String, "/perception/status", 10
        )
        self.timer = self.create_timer(period, self.process_image)

    def process_image(self) -> None:
        input_path = Path(str(self.get_parameter("input_path").value))
        output_path = Path(str(self.get_parameter("output_path").value))
        frame_id = str(self.get_parameter("frame_id").value)
        threshold = float(self.get_parameter("score_threshold").value)

        image = cv2.imread(str(input_path))
        if image is None:
            self.publish_status("error", f"无法读取图片: {input_path}")
            return

        height, width = image.shape[:2]
        # Day 8 先用固定结果练习 ROS 2 边界，真实模型后端在 Day 15 接入。
        score = 0.87
        detections = []
        if score >= threshold:
            detection = Detection2D()
            detection.header.stamp = self.get_clock().now().to_msg()
            detection.header.frame_id = frame_id
            detection.label = "demo-object"
            detection.score = score
            detection.x_min = width // 4
            detection.y_min = height // 4
            detection.x_max = width * 3 // 4
            detection.y_max = height * 3 // 4
            detections.append(detection)

            cv2.rectangle(
                image,
                (detection.x_min, detection.y_min),
                (detection.x_max, detection.y_max),
                (80, 240, 120),
                2,
            )

        message = Detection2DArray()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = frame_id
        message.source_image = str(input_path)
        message.detections = detections
        self.detection_publisher.publish(message)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(output_path), image):
            self.publish_status("error", f"无法写入图片: {output_path}")
            return
        self.publish_status("ok", f"发布 {len(detections)} 个结果")

    def publish_status(self, level: str, detail: str) -> None:
        status = String()
        status.data = json.dumps(
            {"level": level, "detail": detail}, ensure_ascii=False
        )
        self.status_publisher.publish(status)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ImagePerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
