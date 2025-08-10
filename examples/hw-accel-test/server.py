import argparse
import asyncio
import logging
import os
import uuid
from pathlib import Path

import av
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

# Add the project root to the Python path
ROOT = Path(__file__).parent.parent.parent
import sys

sys.path.append(str(ROOT / "src"))

from aiortc.codecs.hw_accel import configure_hardware_acceleration

# --- FastAPI app ---
app = FastAPI()
pcs = set()
# --- Video Generation ---
WIDTH = 640
HEIGHT = 480
FPS = 24
DURATION = 5
TOTAL_FRAMES = DURATION * FPS
VIDEO_FILE = "test.mp4"


def generate_test_video():
    """Generates a test video file if it doesn't exist."""
    if os.path.exists(VIDEO_FILE):
        print(f"✅ Test video '{VIDEO_FILE}' already exists.")
        return

    print(f"🎬 Generating test video '{VIDEO_FILE}'...")
    with av.open(VIDEO_FILE, mode="w") as container:
        stream = container.add_stream("libx264", rate=FPS)
        stream.width = WIDTH
        stream.height = HEIGHT
        stream.pix_fmt = "yuv420p"

        for i in range(TOTAL_FRAMES):
            img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            bar_height = 50
            bar_pos = int((i / TOTAL_FRAMES) * HEIGHT)
            r, g, b = (
                int(255 * (i / TOTAL_FRAMES)),
                int(255 * (1 - (i / TOTAL_FRAMES))),
                128,
            )
            img[bar_pos : bar_pos + bar_height, :] = (r, g, b)
            frame = av.VideoFrame.from_ndarray(img, format="rgb24")
            for packet in stream.encode(frame):
                container.mux(packet)

        for packet in stream.encode():
            container.mux(packet)
    print(f"✅ Test video '{VIDEO_FILE}' created.")


# --- WebRTC and FastAPI Logic ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(Path(__file__).with_name("index.html"), "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get("/client.js", response_class=PlainTextResponse)
async def read_client_js():
    with open(Path(__file__).with_name("client.js"), "r") as f:
        return PlainTextResponse(content=f.read(), status_code=200)


@app.post("/offer")
async def offer(request: Request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = f"PeerConnection({uuid.uuid4()})"
    pcs.add(pc)

    def log_info(msg, *args):
        logging.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.client.host)

    player = MediaPlayer(VIDEO_FILE)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

    # add media track
    if player.video:
        pc.addTrack(player.video)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC demo with hardware acceleration"
    )
    parser.add_argument(
        "--hw-accel",
        action="store_true",
        help="Enable hardware acceleration.",
    )
    parser.add_argument(
        "--codec",
        type=str,
        help='Specify a hardware codec backend, e.g., "videotoolbox", "vaapi", "nvenc".',
    )
    parser.add_argument("--video-file", help="Path to a video file to serve.")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server")
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    # Configure hardware acceleration
    print("-" * 20)
    configure_hardware_acceleration(enabled=args.hw_accel, codec_name=args.codec)
    print("-" * 20)

    # Select video source
    if args.video_file:
        if os.path.exists(args.video_file):
            VIDEO_FILE = args.video_file
            print(f"📹 Serving video from: {VIDEO_FILE}")
        else:
            print(f"❌ Error: Video file not found at '{args.video_file}'")
            sys.exit(1)
    else:
        generate_test_video()

    # Run the server
    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)
