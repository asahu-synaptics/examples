import subprocess
import json
import os
import time
import sys
import warnings
from synap import Network
from synap.preprocessor import Preprocessor
from synap.postprocessor import Classifier

MODEL_PATH = "/usr/share/synap/models/image_classification/imagenet/model/mobilenet_v2_1.0_224_quant/model.synap"
LABELS_FILE = "/usr/share/synap/models/image_classification/imagenet/info.json"

try:
    import gi
    gi.require_version("GUdev", "1.0")
    from gi.repository import GUdev
    GLIB_AVAILABLE = True
except ImportError:
    GLIB_AVAILABLE = False
    warnings.warn("Unable to import gi, camera detection defaulting to /dev/video7")

def get_camera_devices(cam_subsys: str = "video4linux") -> list[str]:
    if not GLIB_AVAILABLE:
        return ["/dev/video7"]

    camera_paths: list[str] = []
    client = GUdev.Client(subsystems=[cam_subsys])
    devices = client.query_by_subsystem(cam_subsys)

    for device in devices:
        bus = device.get_property("ID_BUS")
        if bus == "usb":
            sys_path = device.get_sysfs_path()
            if sys_path:
                index_path = f"{sys_path}/index"
                try:
                    with open(index_path, "r") as f:
                        contents = f.read().strip()
                        index_val = int(contents)

                        if index_val == 0:
                            dev_node = device.get_device_file()
                            if dev_node:
                                camera_paths.append(dev_node)
                except OSError as e:
                    warnings.warn(f"Warning: Error reading {index_path}: {e}")
                except ValueError:
                    warnings.warn(f"Warning: Unexpected contents in {index_path}: {contents}")

    return camera_paths

def capture_photo(device=None, filename="/dev/shm/out.jpg"):
    try:
        device = device or get_camera_devices()[0]
    except IndexError:
        warnings.warn("Valid camera device not found, defaulting to /dev/video7")
        device = "/dev/video7"
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

class ImageClassifier:
    def __init__(self, model_path=MODEL_PATH, labels_file=LABELS_FILE, top_count=5, debug=False):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"'{model_path}' not found")
        self.labels = self.load_labels(labels_file)
        self.network = Network(model_path)
        self.preprocessor = Preprocessor()
        self.classifier = Classifier(top_count=top_count)
        self.debug = debug

    def load_labels(self, labels_file):
        with open(labels_file, "r") as f:
            return json.load(f)["labels"]

    def infer(self, image_path):
        if self.debug:
            print("Net:", MODEL_PATH)
            print("Img:", image_path)
        
        t0 = time.time()
        self.preprocessor.assign(self.network.inputs, image_path)
        t_pre = 1000 * (time.time() - t0)

        t0 = time.time()
        outputs = self.network.predict()
        t_inf = 1000 * (time.time() - t0)

        t0 = time.time()
        result = self.classifier.process(outputs)
        t_post = 1000 * (time.time() - t0)

        tot = t_pre + t_inf + t_post
        if self.debug:
            print(f"Time: {tot:.3f} ms ", end="")
            print(f"(pre: {t_pre:.3f} ms, inf: {t_inf:.3f} ms, post: {t_post:.3f} ms)")
            print("\nClass  Conf   Desc")
            for item in result.items:
                print(f"{item.class_index:5d}{item.confidence:12.4f}  {self.labels[item.class_index]}")
        
        if result.items:
            best = result.items[0]
            return self.labels[best.class_index]
        return None

def main():
    photo_file = "out.jpg"
    if not capture_photo(filename=photo_file):
        print("Photo capture failed.")
        return

    clf = ImageClassifier()
    best_label = clf.infer(photo_file).split(',')[0]
    print(best_label)

if __name__ == "__main__":
    main()
