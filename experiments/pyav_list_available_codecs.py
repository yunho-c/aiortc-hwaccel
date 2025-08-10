import av

# Get all available codecs from the linked FFmpeg library
available_codecs = av.codecs_available

# --- Check for AV1 ---
print("--- AV1 Support ---")
if 'av1' in available_codecs:
    print("✅ Generic AV1 codec is available.")
if 'libdav1d' in available_codecs:
    print("✅ High-performance 'libdav1d' AV1 decoder is available.")
if 'libaom-av1' in available_codecs:
    print("✅ 'libaom' AV1 encoder/decoder is available.")

# --- Check for VP9 ---
print("\n--- VP9 Support ---")
if 'vp9' in available_codecs:
    print("✅ Generic VP9 codec is available.")
if 'libvpx-vp9' in available_codecs:
    print("✅ 'libvpx-vp9' encoder/decoder is available.")

# --- Check for H.264 ---
print("\n--- H.264 Support ---")
if 'h264' in available_codecs:
    print("✅ Generic H.264 codec is available.")
if 'libx264' in available_codecs:
    print("✅ 'libx264' H.264 encoder is available.")

# --- Check for VP8 ---
print("\n--- VP8 Support ---")
if 'vp8' in available_codecs:
    print("✅ Generic VP8 codec is available.")
if 'libvpx' in available_codecs:
    print("✅ 'libvpx' VP8/VP9 encoder/decoder is available.")
