Hardware Acceleration Example
=============================

This example demonstrates how to use the hardware acceleration features in `aiortc`.
It serves a synthetically generated video file over WebRTC to a web browser client,
allowing you to test different encoding backends.

Prerequisites
-------------

You need to install `fastapi` and `uvicorn` to run the server:

.. code-block:: bash

    pip install fastapi uvicorn python-multipart numpy

You will also need a version of PyAV that is compiled with support for the
hardware acceleration backend you wish to use (e.g., VideoToolbox, VAAPI, NVENC).

Running the Example
-------------------

1.  **Start the server:**

    You can run the server with different options to control hardware acceleration.

    *   **To run with software codecs (default):**

        .. code-block:: bash

            python examples/hw-accel-test/server.py

    *   **To enable auto-detected hardware acceleration for your platform:**

        .. code-block:: bash

            python examples/hw-accel-test/server.py --hw-accel

    *   **To enable a specific hardware acceleration backend (e.g., VideoToolbox on macOS):**

        .. code-block:: bash

            python examples/hw-accel-test/server.py --hw-accel --codec videotoolbox

        Replace `videotoolbox` with `vaapi` (Linux) or `nvenc` (NVIDIA) as appropriate.

    *   **To serve a specific video file (e.g., `my_video.mp4`):**
        .. code-block:: bash

            python examples/hw-accel-test/server.py --video-file my_video.mp4

        You can combine this with the `--hw-accel` flags.

2.  **Open the client:**

    Open your web browser and navigate to http://localhost:8080.

3.  **Check the output:**

    The server console will print messages indicating which codecs (hardware or software)
    have been enabled. When you connect with your browser, you should see the
    test video stream playing.
