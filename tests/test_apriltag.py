# tests/test_apriltag.py
import pytest

from apriltag_python import AprilTag
from apriltag_python.tagFamilies import Tag16h5Family, Tag25h9Family, Tag36h11Family


def test_create_detector_family():
    """
    Tests if the create_detector method correctly instantiates
    the specified tag family class.
    """
    detector = AprilTag()

    # Test for tag36h11
    detector.create_detector(family="tag36h11")
    assert isinstance(detector.tagfamily, Tag36h11Family), (
        "Should create a Tag36h11Family instance"
    )

    # Test for tag25h9
    detector.create_detector(family="tag25h9")
    assert isinstance(detector.tagfamily, Tag25h9Family), (
        "Should create a Tag25h9Family instance"
    )

    # Test for tag16h5
    detector.create_detector(family="tag16h5")
    assert isinstance(detector.tagfamily, Tag16h5Family), (
        "Should create a Tag16h5Family instance"
    )


def test_create_detector_unsupported_family():
    """
    Tests if the create_detector method handles an unsupported family.
    Note: This test just checks that it doesn't crash. A more robust
    implementation might raise a specific error.
    """
    detector = AprilTag()
    detector.create_detector(family="unsupported_family")
    assert detector.tagfamily is None, (
        "Tag family should be None for unsupported families"
    )
    detector.create_detector(family="unsupported_family")
    assert detector.tagfamily is None, (
        "Tag family should be None for unsupported families"
    )
    assert detector.tagfamily is None, (
        "Tag family should be None for unsupported families"
    )
