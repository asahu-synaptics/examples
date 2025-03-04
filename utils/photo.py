import subprocess

def capture_photo(device="/dev/video7", filename="out.jpg"):
    # Set the video format to MJPG at 640x480.
    fmt_cmd = [
        "v4l2-ctl",
        f"--device={device}",
        "--set-fmt-video=width=640,height=480,pixelformat=MJPG"
    ]
    try:
        subprocess.run(fmt_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error setting format:")
        print(e.stderr)
        return False

    # Capture one frame to a file.
    capture_cmd = [
        "v4l2-ctl",
        f"--device={device}",
        "--stream-mmap",
        "--stream-count=1",
        f"--stream-to={filename}"
    ]
    try:
        subprocess.run(capture_cmd, capture_output=True, text=True, check=True)
        # print(f"Image saved as {filename}")
        return True
    except subprocess.CalledProcessError as e:
        print("Error capturing image:")
        print(e.stderr)
        return False

if __name__ == "__main__":
    capture_photo()
