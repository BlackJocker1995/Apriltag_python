# Apriltag python


## Apriltag
AprilTag is a visual fiducial system, useful for a wide variety of tasks including augmented reality, robotics, and camera calibration. Targets can be created from an ordinary printer, and the AprilTag detection software computes the precise 3D position, orientation, and identity of the tags relative to the camera. Implementations are available in Java, as well as in C. Notably, the C implementation has no external dependencies and is designed to be easily included in other applications, as well as portable to embedded devices. Real-time performance can be achieved even on cell-phone grade processors.

The two main papers to refer to understand the apriltag algorithm are the following:

1. IROS 2016 - [AprilTag 2: Efficient and robust fiducial detection](https://april.eecs.umich.edu/media/pdfs/wang2016iros.pdf): this is the paper which refers to the version of the algorithm that we want to use

2. ICRA 2011 - [AprilTag: A robust and flexible visual fiducial system](https://ieeexplore.ieee.org/abstract/document/5979561/): this is the paper which explains how the first version of the algorithm works

## Apriltag python
This program is base on apriltag without any c extra plugin.And this program encompass tag36h11 tag25h9 and tag16h5.If you han any idea about enchance this program`s function,you can modify whatever you want.
Just support tag36h11,tag25h9,tag16h5.

## Installation and Usage

You can use `pip` or `uv` to install the dependencies and run the project.

### Using `pip`

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install .
    ```
    For development (including tests):
    ```bash
    pip install ".[dev]"
    ```

3.  **Run tests:**
    ```bash
    pytest
    ```

### Using `uv` (Recommended)

`uv` is a fast Python package installer and resolver.

1.  **Install `uv`:**
    ```bash
    pip install uv
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install ".[dev]"
    ```

3.  **Run tests:**
    ```bash
    uv run pytest
    ```

## Running the detection on an image

To run the AprilTag detection on the sample image (`tests/tag.png`), you can execute the `test_detection.py` test. This will generate an output image with the detection results in `test_outputs/detection_result.png`.

Using `pytest`:
```bash
pytest tests/test_detection.py
```

Or using `uv`:
```bash
uv run pytest tests/test_detection.py
```
