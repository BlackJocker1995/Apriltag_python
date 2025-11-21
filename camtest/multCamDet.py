import cv2
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger
from mpl_toolkits.mplot3d import Axes3D

from apriltag_python import AprilTag
from apriltag_python import tagUtils as tud


class MultiCamDet(object):
    """
    A class for detecting AprilTags using multiple cameras, either from live video
    streams or from pre-recorded image files. It can calculate the 3D coordinates
    of a tag based on distances measured by multiple cameras.
    """

    def __init__(self, config, debug=False):
        """
        Initializes the multi-camera detector.

        :param config: A dictionary containing configuration parameters.
                       Expected keys: 'num_cameras', 'resolution', 'distance_const', 'edge_length'.
        :param debug: If True, enables debug output.
        """
        self.config = config
        self.n = config.get("num_cameras", 4)
        self.debug = debug

        self.videocaptures = []
        self.videowriters = []
        self.frames = []
        self.__filenames = []

        self.detector = AprilTag().create_detector()

    def __init_video_captures(self):
        """Initializes video capture objects for all cameras."""
        width, height = self.config.get("resolution", (1920, 1080))
        for i in range(self.n):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.videocaptures.append(cap)
            else:
                logger.warning(f"Camera {i} could not be opened.")

        if not self.videocaptures:
            logger.error("No cameras were successfully opened.")
            exit(1)
        self.n = len(self.videocaptures)  # Update n to the number of opened cameras

    def __init_video_writers(self, output_dir="."):
        """
        Initializes video writer objects for all cameras.

        :param output_dir: Directory to save the output video files.
        """
        width, height = self.config.get("resolution", (1920, 1080))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Use modern FOURCC
        for i in range(self.n):
            filepath = f"{output_dir}/{i}.avi"
            out = cv2.VideoWriter(filepath, fourcc, 10, (width, height))
            self.videowriters.append(out)

    def __init_file_reader(self, base_path="3dpicture/"):
        """
        Initializes file paths for reading images.

        :param base_path: The base path where image folders are located.
        """
        for index in range(self.n):
            filename = f"{base_path}{index}_"
            self.__filenames.append(filename)

    def __grab_frames_from_cams(self):
        """Grabs the next frame from all video captures. Returns False if any fails."""
        for capture in self.videocaptures:
            if not capture.grab():
                return False
        return True

    def __retrieve_frames_from_cams(self):
        """Retrieves the grabbed frames from all cameras."""
        self.frames = []
        for capture in self.videocaptures:
            flag, frame = capture.retrieve()
            if flag:
                self.frames.append(frame)
            else:
                logger.warning("Could not retrieve frame from a camera.")

    def __read_frames_from_files(self, image_index):
        """
        Reads frames for a specific index from files.

        :param image_index: The index of the image set to read.
        """
        self.frames = []
        for i in range(self.n):
            filepath = f"{self.__filenames[i]}{image_index}.jpg"
            frame = cv2.imread(filepath)
            if frame is not None:
                self.frames.append(frame)
            else:
                logger.warning(f"Could not read image {filepath}")

    def __save_frames_to_video(self):
        """Saves the retrieved frames to their respective video files."""
        for frame, out in zip(self.frames, self.videowriters):
            if frame is not None:
                out.write(frame)

    def __detect_tags_and_distances(self):
        """
        Detects AprilTags in the current batch of frames and calculates their distances.

        :return: A numpy array of [camera_index, tag_id, distance] for the closest tag in each frame.
        """
        result = []
        cam_index = 0
        distance_const = self.config.get("distance_const", 121938.1)

        for frame in self.frames:
            if frame is None:
                cam_index += 1
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detections = self.detector.detect(gray)

            if not detections:
                cam_index += 1
                continue

            distances = []
            tag_ids = []
            for detection in detections:
                dis = tud.get_distance(detection.homography, distance_const)
                distances.append(dis)
                tag_ids.append(detection.tag_id)

            min_index = np.argmin(distances)
            result.append([cam_index, tag_ids[min_index], distances[min_index]])
            cam_index += 1

        return np.array(result)

    def process_from_image_files(self, num_images, base_path="3dpicture/"):
        """
        Processes a sequence of images from files to determine 3D coordinates.
        Assumes 4 cameras are used.
        """
        self.__init_file_reader(base_path)
        ax = plt.subplot(111, projection="3d")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_xlim(-20, 120)
        ax.set_ylim(-20, 120)
        ax.set_zlim(-20, 120)

        edge_length = self.config.get("edge_length", 1100)

        for index in range(num_images):
            self.__read_frames_from_files(index)
                logger.info(
                    f"Skipping index {index}: Not enough images found (need 4)."
                )
                logger.info(f"Skipping index {index}: Not enough images found (need 4).")
                continue

            result = self.__detect_tags_and_distances()

            if len(result) == 4:
                # This mapping depends on the physical setup of the cameras.
                # Assuming result[0] is cam0, result[1] is cam1, etc.
                # And the geometry is (cam0, cam1, cam3) for sovle_coord
                try:
                    cam0_dist = result[result[:, 0] == 0][0, 2]
                    cam1_dist = result[result[:, 0] == 1][0, 2]
                    cam2_dist = result[result[:, 0] == 2][0, 2]
                    cam3_dist = result[result[:, 0] == 3][0, 2]

                    x, y, z_est = tud.sovle_coord(
                        cam0_dist, cam1_dist, cam3_dist, edge=edge_length
                    )
                    z = tud.verify_z(x, y, cam2_dist, edge=edge_length)

                    ax.scatter(x, y, z)
                    logger.info(f"Coordinates: x={x:.2f}, y={y:.2f}, z={z:.2f}")
                except IndexError:
                    logger.info(
                        f"Skipping index {index}: Missing detection from one of the 4 cameras."
                    )

        plt.show()

    def process_from_live_video(self):
        """
        Processes live video from cameras to determine 3D coordinates in real-time.
        Assumes 4 cameras are used.
        """
        self.__init_video_captures()

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_xlim(-200, 1200)
        ax.set_ylim(-200, 1200)
        ax.set_zlim(-200, 1200)

        edge_length = self.config.get("edge_length", 1100)

        while True:
            if not self.__grab_frames_from_cams():
                break
            self.__retrieve_frames_from_cams()

            result = self.__detect_tags_and_distances()

            if len(result) == 4:
                try:
                    # Similar to file processing, assuming a specific camera setup.
                    cam0_dist = result[result[:, 0] == 0][0, 2]
                    cam1_dist = result[result[:, 0] == 1][0, 2]
                    cam2_dist = result[result[:, 0] == 2][0, 2]
                    cam3_dist = result[result[:, 0] == 3][0, 2]

                    x, y, _ = tud.sovle_coord(
                        cam0_dist, cam1_dist, cam3_dist, edge=edge_length
                    )
                    z = tud.verify_z(x, y, cam2_dist, edge=edge_length)

                    logger.info(f"Coordinates: x={x:.2f}, y={y:.2f}, z={z:.2f}")
                    ax.scatter(x, y, z)
                    plt.pause(0.001)
                except IndexError:
                    # This can happen if a tag is lost in one of the frames
                    logger.info("Waiting for detections from all 4 cameras...")

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        plt.show()

    def __del__(self):
        """Releases all video capture and writer resources."""
        for cap in self.videocaptures:
            cap.release()
        for out in self.videowriters:
            out.release()
        cv2.destroyAllWindows()


def main():
    # Configuration for the detector
    config = {
        "num_cameras": 4,
        "resolution": (1920, 1080),
        "distance_const": 121938.1,  # This needs calibration: focal_length_px * tag_size_m
        "edge_length": 1100,  # The distance between cameras in your setup
    }

    # --- To run with live cameras ---
    # logger.info("Starting live detection from cameras...")
    # cam_detector = MultiCamDet(config)
    # cam_detector.process_from_live_video()

    # --- To run with pre-recorded images ---
    logger.info("Starting detection from image files...")
    file_detector = MultiCamDet(config)
    # Assumes images are in '3dpicture/' and there are 5 sets of them.
    file_detector.process_from_image_files(num_images=5, base_path="3dpicture/")


if __name__ == "__main__":
    main()
