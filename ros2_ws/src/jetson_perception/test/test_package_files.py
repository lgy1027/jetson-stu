from pathlib import Path

import yaml


PACKAGE_ROOT = Path(__file__).parents[1]


def test_parameter_file_has_required_fields() -> None:
    data = yaml.safe_load(
        (PACKAGE_ROOT / "config" / "offline_perception.yaml").read_text()
    )
    parameters = data["image_perception"]["ros__parameters"]
    assert 0.0 <= parameters["score_threshold"] <= 1.0
    assert parameters["publish_period"] > 0
    assert parameters["frame_id"]


def test_launch_and_resource_files_exist() -> None:
    assert (PACKAGE_ROOT / "launch" / "offline_perception.launch.py").is_file()
    assert (PACKAGE_ROOT / "resource" / "jetson_perception").is_file()
