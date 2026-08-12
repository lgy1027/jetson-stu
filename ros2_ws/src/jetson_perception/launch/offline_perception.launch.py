from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    package_share = Path(get_package_share_directory("jetson_perception"))
    parameter_file = package_share / "config" / "offline_perception.yaml"

    return LaunchDescription(
        [
            Node(
                package="jetson_perception",
                executable="image_perception",
                name="image_perception",
                parameters=[str(parameter_file)],
                output="screen",
            ),
            Node(
                package="jetson_perception",
                executable="detection_listener",
                name="detection_listener",
                output="screen",
            ),
        ]
    )
