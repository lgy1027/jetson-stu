import numpy as np

from perception.image_ops import annotate_detections, bgr_to_normalized_rgb, center_crop, resize_keep_aspect


def test_center_crop_returns_requested_shape():
    # 裁剪参数是宽、高，NumPy shape 则是高、宽、通道。
    image = np.zeros((20, 40, 3), dtype=np.uint8)
    result = center_crop(image, 12, 10)
    assert result.shape == (10, 12, 3)


def test_center_crop_rejects_oversized_request():
    # 越界裁剪应直接报错，不能静默返回尺寸不对的结果。
    image = np.zeros((20, 40, 3), dtype=np.uint8)
    try:
        center_crop(image, 41, 10)
    except ValueError as error:
        assert "exceeds image" in str(error)
    else:
        raise AssertionError("oversized crop should fail")


def test_resize_preserves_aspect_ratio():
    # 原图 2:1，宽度缩小到 80 后，高度应为 40。
    image = np.zeros((100, 200, 3), dtype=np.uint8)
    result = resize_keep_aspect(image, 80)
    assert result.shape == (40, 80, 3)


def test_bgr_to_normalized_rgb_changes_order_and_dtype():
    # BGR 的蓝、绿、红顺序转换成 RGB，并归一化到 0~1。
    image = np.array([[[0, 128, 255]]], dtype=np.uint8)
    result = bgr_to_normalized_rgb(image)
    assert result.dtype == np.float32
    assert np.allclose(result[0, 0], [1.0, 128 / 255.0, 0.0])


def test_bgr_to_normalized_rgb_rejects_non_uint8():
    # 已经是浮点数的输入不能再次按 uint8 图片处理。
    image = np.zeros((2, 2, 3), dtype=np.float32)
    try:
        bgr_to_normalized_rgb(image)
    except ValueError as error:
        assert "expected uint8" in str(error)
    else:
        raise AssertionError("non-uint8 image should fail")


def test_annotation_does_not_mutate_input():
    # 画框应修改副本，原始图片留给后续处理使用。
    image = np.zeros((80, 120, 3), dtype=np.uint8)
    original = image.copy()
    result = annotate_detections(image, [{"label": "demo", "score": 0.8, "bbox_xyxy": [10, 20, 70, 60]}])
    assert np.array_equal(image, original)
    assert not np.array_equal(result, original)
