from glob import glob
from setuptools import find_packages, setup


package_name = "jetson_perception"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="lgy1027",
    maintainer_email="lgy10271416@gmail.com",
    description="Offline perception nodes used by the Jetson embodied AI course.",
    license="Apache-2.0",
    # colcon test 会据此使用 pytest 收集 test/ 目录中的测试。
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "hello_publisher = jetson_perception.hello_publisher:main",
            "hello_subscriber = jetson_perception.hello_subscriber:main",
            "detection_publisher = jetson_perception.detection_publisher:main",
            "detection_listener = jetson_perception.detection_listener:main",
            "image_perception = jetson_perception.image_perception_node:main",
        ],
    },
)
