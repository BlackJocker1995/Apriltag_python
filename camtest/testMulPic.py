import apriltag as ap
import cv2
import matplotlib.pyplot as plt
import numpy as np
import tagUtils as tud
from mpl_toolkits.mplot3d import Axes3D


def process_images(config):
    """
    Processes sets of images from multiple cameras to calculate the 3D position of an AprilTag.

    This script is designed for a specific experimental setup where multiple cameras capture
    images of the same tag, and the 3D coordinates are triangulated from the calculated
    distances.

    :param config: A dictionary containing configuration parameters.
    """
    base_path = config.get("base_path", "../3dpicture6")
    num_images = config.get("num_images", 5)
    distance_const = config.get("distance_const", 121938.0923)
    edge_length = config.get("edge_length", 1000)

    # Create the detector once outside the loop
    detector = ap.Apriltag()
    detector.create_detector(
        sigma=0.8, thresholding="adaptive", debug=False, downsampling=False
    )

    results = []

    # Setup 3D plot
    ax = plt.subplot(111, projection="3d")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_xlim(-200, 1200)
    ax.set_ylim(-200, 1200)
    ax.set_zlim(-200, 1200)

    for index in range(num_images):
        # Define filenames for the 4 cameras for the current index
        filenames = [f"{base_path}/{i}_{index}.jpg" for i in range(4)]
        frames = [cv2.imread(fn) for fn in filenames]

        if any(frame is None for frame in frames):
            print(
                f"Warning: Skipping index {index}, one or more images could not be read."
            )
            continue

        # Detect tags in all frames
        detections = [detector.detect(frame) for frame in frames]

        if any(len(d) < 1 for d in detections):
            print(
                f"Warning: Skipping index {index}, no detections in one or more frames."
            )
            continue

        # Calculate the minimum distance to a tag in each frame
        # Note: The original script had 'add' which was 0, so it's removed for clarity.
        distances = [tud.get_min_distance(d, distance_const) for d in detections]

        # Unpack distances for clarity
        dis0, dis1, dis2, dis3 = distances

        # --- Start of experiment-specific coordinate calculation ---
        # This logic is highly specific to the geometric setup of the cameras.
        # It appears to calculate the position from three different perspectives and average them.

        # Perspective 1
        x1, y1, _ = tud.sovle_coord(dis0, dis1, dis3, edge_length)
        z1 = tud.verify_z(x1, y1, dis2, edge_length)

        # Perspective 2
        x2, y2, _ = tud.sovle_coord(dis3, dis0, dis2, edge_length)
        z2 = tud.verify_z(x2, y2, dis1, edge_length)

        # Perspective 3
        x3, y3, _ = tud.sovle_coord(dis2, dis3, dis1, edge_length)
        z3 = tud.verify_z(x3, y3, dis0, edge_length)

        # The original script performs some coordinate transformations.
        # These are likely to align the coordinate systems of the different perspectives.
        p1 = np.array([x1, y1, z1])
        p2 = np.array([y2, edge_length - x2, z2])  # Transformation
        p3 = np.array([edge_length - x3, edge_length - y3, z3])  # Transformation

        # Average the results from the three perspectives
        final_point = (p1 + p2 + p3) / 3.0
        results.append(final_point)

        print(f"\nIndex {index}:")
        print(f"  Perspective 1: {p1}")
        print(f"  Perspective 2: {p2}")
        print(f"  Perspective 3: {p3}")
        print(f"  => Averaged Point: {final_point}")

        # Plot the individual and averaged points
        ax.scatter(p1[0], p1[1], p1[2], c="r", marker="o")
        ax.scatter(p2[0], p2[1], p2[2], c="g", marker="^")
        ax.scatter(p3[0], p3[1], p3[2], c="b", marker="s")
        ax.scatter(
            final_point[0], final_point[1], final_point[2], c="black", marker="x", s=100
        )
        plt.pause(0.01)
        # --- End of experiment-specific coordinate calculation ---

    print("\n--- Final Results ---")
    for i in range(len(results) - 1, 0, -1):
        # This calculates the movement between consecutive averaged points,
        # comparing it to an expected movement of 100 units.
        movement = np.linalg.norm(results[i] - results[i - 1])
        print(f"Movement from index {i - 1} to {i}: {movement:.2f} (Expected ~100)")

    plt.show()


def main():
    """Main function to run the image processing."""
    config = {
        "base_path": "../3dpicture6",
        "num_images": 5,
        "distance_const": 121938.0923,
        "edge_length": 1000,
    }
    process_images(config)


if __name__ == "__main__":
if __name__ == '__main__':
    main()
