import os

import cv2
import numpy as np
from loguru import logger

from apriltag_python import AprilTag


def run_detection():
    """
    This function runs the detection pipeline on a sample image 'tag.png'.
    It saves a visual result.
    """
    # 1. Initialize the detector
    detector = AprilTag()
    # Assuming tag.png is from the tag36h11 family, which is a common default
    detector.create_detector(family="tag36h11")

    # 2. Load the image from its new location
    image_path = "tests/tag.png"
    frame = cv2.imread(image_path)
    if frame is None:
        logger.info(f"Failed to load {image_path}.")
        return

    # 3. Detect tags
    detections = detector.detect(frame)

    # 4. Assert the results
    if detections is None:
        logger.info("Detection returned None")
        return
    if len(detections) != 1:
        logger.info(f"Expected 1 tag, but found {len(detections)}")
        return

    logger.info(f"Detected {len(detections)} tag(s).")

    # 5. Draw results and save the output image
    detection = detections[0]
    # Extract corner points
    points = detection.points.astype(int)
    # Draw the bounding box
    cv2.polylines(frame, [points], isClosed=True, color=(0, 255, 0), thickness=2)
    # Draw the tag ID
    tag_id = detection.id
    cv2.putText(
        frame,
        str(tag_id),
        (
            points[0][0][0],
            points[0][0][1] - 10,
        ),  # Position the text above the top-left corner
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,  # font scale
        (0, 0, 255),  # font color
        2,  # thickness
    )

    # Save the image with detection results
    output_path = "test_outputs/detection_result.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, frame)
    logger.info(f"Detection result saved to {output_path}")


if __name__ == "__main__":
    run_detection()
