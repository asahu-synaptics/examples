#!/usr/bin/env python3
import subprocess
import json
import os
import time
from synap import Network
from synap.preprocessor import Preprocessor
from synap.postprocessor import Classifier

MODEL_PATH = "/usr/share/synap/models/image_classification/imagenet/model/mobilenet_v2_1.0_224_quant/model.synap"
LABELS_FILE = "/usr/share/synap/models/image_classification/imagenet/info.json"

def capture_photo(device="/dev/video7", filename="captured.jpg"):
    # Set video format to MJPG at 640x480.
    fmt_cmd = [
        "v4l2-ctl",
        f"--device={device}",
        "--set-fmt-video=width=640,height=480,pixelformat=MJPG"
    ]
    try:
        subprocess.run(fmt_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error in set format:")
        print(e.stderr)
        return False

    # Capture one frame.
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
        print("Error in capture:")
        print(e.stderr)
        return False

class ImageClassifier:
    def __init__(self, model_path=MODEL_PATH, labels_file=LABELS_FILE, top_count=5):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"'{model_path}' not found")
        self.labels = self.load_labels(labels_file)
        self.network = Network(model_path)
        self.preprocessor = Preprocessor()
        self.classifier = Classifier(top_count=top_count)

    def load_labels(self, labels_file):
        with open(labels_file, "r") as f:
            return json.load(f)["labels"]

    def infer(self, image_path):
        # print("Net:", MODEL_PATH)
        # print("Img:", image_path)

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
        # print(f"Time: {tot:.3f} ms ", end="")
        # print(f"(pre: {t_pre * 1000:.3f} us, inf: {t_inf * 1000:.3f} us, post: {t_post * 1000:.3f} us)")

        # print("\nClass  Conf   Desc")
        # for item in result.items:
        #     print(f"{item.class_index:5d}{item.confidence:12.4f}  {self.labels[item.class_index]}")
        
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
    best_label = clf.infer(photo_file)
    print(best_label)

if __name__ == "__main__":
    main()
