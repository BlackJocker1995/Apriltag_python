"""
This script launches the VisPy-based 3D visualization.

It imports the Canvas class from the tagVisual module, creates an instance,
and runs the VisPy application loop. The Canvas itself contains the logic
for rendering a 3D scene and plotting the results of the AprilTag detection
from pre-recorded images.
"""

from loguru import logger
from vispy import app

from apriltag_python.tagVisual import Canvas

if __name__ == "__main__":
    logger.info("Launching VisPy 3D visualization canvas...")
    c = Canvas(title="AprilTag 3D Visualization")
    app.run()
