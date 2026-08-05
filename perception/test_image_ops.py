import numpy as np

from perception.image_ops import center_crop, resize_keep_aspect


def test_center_crop_returns_requested_shape():
    image = np.zeros((20, 40, 3), dtype=np.uint8)
    result = center_crop(image, 12, 10)
    assert result.shape == (10, 12, 3)


def test_center_crop_rejects_oversized_request():
    image = np.zeros((20, 40, 3), dtype=np.uint8)
    try:
        center_crop(image, 41, 10)
    except ValueError as error:
        assert "exceeds image" in str(error)
    else:
        raise AssertionError("oversized crop should fail")


def test_resize_preserves_aspect_ratio():
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    result = resize_keep_aspect(image, 80)
    assert result.shape == (40, 80, 3)
