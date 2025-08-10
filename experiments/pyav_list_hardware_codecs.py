import av
import re

def find_hardware_codecs():
    """
    Finds and prints all available codecs that appear to be
    hardware-accelerated based on their names.
    """
    # Common patterns in hardware-accelerated codec names
    hw_patterns = [
        '_nvenc', '_nvdec', '_cuvid', # NVIDIA
        '_qsv',                       # Intel Quick Sync
        '_vaapi',                     # VAAPI (Linux)
        '_videotoolbox',              # Apple VideoToolbox
        '_d3d11va', '_d3d11va2',      # Direct3D (Windows)
        '_opencl',
    ]

    available_codecs = av.codecs_available
    hw_encoders = set()
    hw_decoders = set()

    print(f"{available_codecs=}")  # DEBUG

    print("🔎 Searching for available hardware-accelerated codecs...")

    for codec_name in available_codecs:
        if any(pattern in codec_name for pattern in hw_patterns):
            try:
                # Check if it's an encoder
                codec = av.codec.Codec(codec_name, 'w')
                hw_encoders.add(codec.long_name)
            except ValueError:
                # If it's not an encoder, it must be a decoder
                try:
                    codec = av.codec.Codec(codec_name, 'r')
                    hw_decoders.add(codec.long_name)
                except ValueError:
                    pass # Some codecs might be neither (e.g., bitstream filters)

    if hw_encoders:
        print("\n✅ Available Hardware Encoders:")
        for name in sorted(hw_encoders):
            print(f"  - {name}")
    else:
        print("\n❌ No hardware encoders found.")

    if hw_decoders:
        print("\n✅ Available Hardware Decoders:")
        for name in sorted(hw_decoders):
            print(f"  - {name}")
    else:
        print("\n❌ No hardware decoders found.")


if __name__ == "__main__":
    find_hardware_codecs()
