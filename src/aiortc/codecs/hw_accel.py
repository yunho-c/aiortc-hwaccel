import sys
import traceback
from functools import partial
from typing import Optional

import av

from . import VIDEO_DECODERS, VIDEO_ENCODERS
from .h264 import H264Decoder, H264Encoder
from .vpx import Vp8Decoder, Vp8Encoder

# Platform-specific codec names
# The first one in the list is the preferred one.
# Each entry is a tuple of (encoder, decoder)
PLATFORM_CODECS = {
    "darwin": {
        "h264": ("h264_videotoolbox", "h264_videotoolbox"),
    },
    "linux": {
        "h264": ("h264_vaapi", "h264_vaapi"),
        "vp8": ("vp8_vaapi", "vp8_vaapi"),
    },
    # Add other platforms and backends like nvenc/d3d11va2 here
}

# Mapping from simple names to PyAV codec names
# This allows users to pass a simple name like "videotoolbox"
CODEC_NAME_MAP = {
    "videotoolbox": {
        "h264": ("h264_videotoolbox", "h264_videotoolbox"),
    },
    "vaapi": {
        "h264": ("h264_vaapi", "h264_vaapi"),
        "vp8": ("vp8_vaapi", "vp8_vaapi"),
    },
    "nvenc": {
        "h264": ("h264_nvenc", "h264_cuvid"),
    },
}

# Default software codecs
DEFAULT_FACTORIES = {
    "h264": (H264Encoder, H264Decoder),
    "vp8": (Vp8Encoder, Vp8Decoder),
}


def _probe_codec(name: str, is_encoder: bool) -> bool:
    """Check if a PyAV codec is available."""
    try:
        if is_encoder:
            av.CodecContext.create(name, "w")
        else:
            av.CodecContext.create(name, "r")
        return True
    except Exception:
        # print("Error:", e)
        traceback.print_exc()
        return False


def configure_hardware_acceleration(
    enabled: bool = True, codec_name: Optional[str] = None
):
    """
    Enable or disable hardware-accelerated video codecs.
    If `enabled` is `True`, this function will attempt to use a hardware-accelerated
    codec. If `codec_name` is provided (e.g., "videotoolbox", "vaapi", "nvenc"),
    it will use that specific backend. If `codec_name` is not provided, it will
    try to auto-detect a suitable one for the current platform.
    If `enabled` is `False`, it will revert to the default software codecs.
    :param enabled: Whether to enable hardware acceleration.
    :param codec_name: The name of the hardware acceleration backend to use.
    """
    if not enabled:
        # Revert to software codecs
        for codec, (encoder_cls, decoder_cls) in DEFAULT_FACTORIES.items():
            VIDEO_ENCODERS[codec] = encoder_cls
            VIDEO_DECODERS[codec] = decoder_cls
        print("Hardware acceleration disabled. Reverted to software codecs.")
        return

    video_formats = ["h264", "vp8"]
    backend_map = {}

    if codec_name:
        if codec_name in CODEC_NAME_MAP:
            backend_map = CODEC_NAME_MAP[codec_name]
        else:
            print(f"Warning: Unknown codec_name '{codec_name}' provided.")
    else:
        backend_map = PLATFORM_CODECS.get(sys.platform, {})

    for fmt in video_formats:
        encoder_cls, decoder_cls = DEFAULT_FACTORIES[fmt]
        hw_encoder_name, hw_decoder_name = backend_map.get(fmt, (None, None))

        # print(f"{hw_encoder_name=}, {hw_decoder_name=}")  # DEBUG

        # Configure encoder
        if hw_encoder_name and _probe_codec(hw_encoder_name, is_encoder=True):
            VIDEO_ENCODERS[fmt] = partial(encoder_cls, hw_encoder_name)
            print(f"Enabled {fmt.upper()} hardware encoder: {hw_encoder_name}")
        else:
            VIDEO_ENCODERS[fmt] = encoder_cls
            if hw_encoder_name:
                print(
                    f"{fmt.upper()} hardware encoder '{hw_encoder_name}' not available."
                )

        # Configure decoder
        if hw_decoder_name and _probe_codec(hw_decoder_name, is_encoder=False):
            VIDEO_DECODERS[fmt] = partial(decoder_cls, hw_decoder_name)
            print(f"Enabled {fmt.upper()} hardware decoder: {hw_decoder_name}")
        else:
            VIDEO_DECODERS[fmt] = decoder_cls
            if hw_decoder_name:
                print(
                    f"{fmt.upper()} hardware decoder '{hw_decoder_name}' not available."
                )
