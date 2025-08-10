import os
import time

import av
import numpy as np

# --- Configuration ---
WIDTH = 640
HEIGHT = 480
FPS = 24
DURATION = 5  # seconds
TOTAL_FRAMES = DURATION * FPS

# --- Utility for Timing ---
class PerfTimer:
    """A simple context manager to measure execution time."""
    def __init__(self, name):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        self.duration = end_time - self.start_time
        print(f"⏱️  '{self.name}' took: {self.duration:.4f} seconds")

def generate_synthetic_video_frames():
    """
    Generates a series of VideoFrame objects with a simple pattern.
    This creates a test video in memory to avoid file I/O for the source.
    """
    print(f"🎬 Generating {TOTAL_FRAMES} synthetic video frames...")
    frames = []
    for i in range(TOTAL_FRAMES):
        # Create a blank numpy array for the image
        img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        # Create a simple moving bar animation
        bar_height = 50
        bar_pos = int((i / TOTAL_FRAMES) * HEIGHT)

        # Calculate RGB values that change over time
        r = int(255 * (i / TOTAL_FRAMES))
        g = int(255 * (1 - (i / TOTAL_FRAMES)))
        b = 128

        img[bar_pos:bar_pos + bar_height, :] = (r, g, b)

        # Convert the numpy array to a PyAV VideoFrame
        frame = av.VideoFrame.from_ndarray(img, format='rgb24')
        frames.append(frame)

    print("✅ Frames generated.\n")
    return frames

def benchmark_codec(codec_name, filename, frames):
    """
    Encodes a list of frames to a file and then decodes it,
    measuring the time for each operation.
    """
    print(f"--- Benchmarking Codec: {codec_name} ---")

    # === ENCODING ===
    try:
        with av.open(filename, mode='w') as container:
            # Add a video stream to the container
            stream = container.add_stream(codec_name, rate=FPS)
            stream.width = WIDTH
            stream.height = HEIGHT
            # Most modern codecs work best with yuv420p pixel format
            stream.pix_fmt = 'yuv420p'

            with PerfTimer(f"Encoding to {codec_name}"):
                # Loop through the frames, encode them, and write to the container
                for frame in frames:
                    for packet in stream.encode(frame):
                        container.mux(packet)

                # Flush any remaining packets from the encoder
                for packet in stream.encode():
                    container.mux(packet)
    except av.error.ValueError as e:
        print(f"❌ ERROR: Could not find or initialize encoder '{codec_name}'.")
        print("   Please ensure your FFmpeg build supports this codec.")
        print(f"   Original error: {e}\n")
        return

    # Report file size
    if os.path.exists(filename):
        file_size_bytes = os.path.getsize(filename)
        file_size_kb = file_size_bytes / 1024
        print(f"   📄 Resulting file size: {file_size_kb:.2f} KB")

    # === DECODING ===
    try:
        with av.open(filename, mode='r') as container:
            frame_count = 0
            with PerfTimer(f"Decoding from {codec_name}"):
                # Simply iterate through the decoder to process all frames
                for frame in container.decode(video=0):
                    frame_count += 1

            print(f"   Decoded {frame_count} frames.")

    except av.error.ValueError as e:
        print(f"❌ ERROR: Could not find or initialize decoder for the video in '{filename}'.")
        print(f"   Original error: {e}\n")
        return
    finally:
        # Clean up the created video file
        if os.path.exists(filename):
            os.remove(filename)
            print(f"   Cleaned up {filename}.\n")



if __name__ == "__main__":
    # Generate the source video frames once
    video_frames = generate_synthetic_video_frames()

    # --- Run Benchmarks ---
    # Benchmark AV1 using the libaom encoder. The .mkv container is flexible.
    benchmark_codec('libaom-av1', 'test_video_av1.mkv', video_frames)

    # Benchmark VP9 using the libvpx encoder. The .webm container is standard for VP9.
    benchmark_codec('libvpx-vp9', 'test_video_vp9.webm', video_frames)

    # Benchmark H.264 using the default encoder (often libx264). The .mp4 container is common.
    benchmark_codec('h264', 'test_video_h264.mp4', video_frames)

    # Benchmark VP8 using the default encoder (often libvpx). The .webm container is standard for VP8.
    benchmark_codec('vp8', 'test_video_vp8.webm', video_frames)

    print("--- Benchmark Complete ---")

