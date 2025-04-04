"""
Run a GStreamer demo.

Requires a valid input source (video / camera / RTSP) and SyNAP inference model.
"""

from typing import Any
import argparse
import sys

from gst.pipeline import GstPipelineGenerator
from utils.user_input import *
from utils.model_info import *


def main(args: argparse.Namespace) -> None:
    gst_params: dict[str, Any] = {}

    try:
        if args.input_dims:
            gst_params["inp_w"], gst_params["inp_h"] = [
                int(d) for d in args.input_dims.split("x")
            ]

        if not (
            inp_src_info := get_inp_src_info(
                gst_params.get("inp_w", None),
                gst_params.get("inp_h", None),
                args.input,
                args.input_codec if args.input else None,
            )
        ):
            sys.exit(1)
        (
            gst_params["inp_type"],
            gst_params["inp_src"],
            gst_params["inp_codec"],
            gst_params["codec_elems"],
        ) = inp_src_info

        gst_params["inf_model"] = get_inf_model(args.model)
        model_inp_dims = get_model_input_dims(gst_params["inf_model"])
        if not model_inp_dims:
            sys.exit(1)
        gst_params["inf_w"], gst_params["inf_h"] = model_inp_dims
        gst_params["inf_skip"] = get_int_prop(
            "How many frames to skip between each inference",
            args.inference_skip if args.model else None,
            1,
        )
        gst_params["inf_max"] = get_int_prop(
            "Maximum number of detections returned per frame",
            args.num_inferences if args.model else None,
            5,
        )
        gst_params["inf_thresh"] = get_float_prop(
            "Confidence threshold for inferences",
            args.confidence_threshold if args.model else None,
            0.5,
            0.0,
            1.0,
        )
        gst_params["inf_labels"] = get_file_prop(
            "Class labels file",
            args.labels if args.model else None,
            "/usr/share/synap/models/object_detection/coco/info.json",
        )
        gst_params["fullscreen"] = (
            args.fullscreen
            if args.fullscreen is not None
            else get_bool_prop("Launch demo in fullscreen?")
        )
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()

    gen: GstPipelineGenerator = GstPipelineGenerator(gst_params)

    gen.make_pipeline()
    gen.pipeline.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="NOTE: The script will interactively ask for necessary info not provided via command line.",
    )

    # Input video source: can be a camera device, video file, or RTSP stream URL
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="SRC",
        help="Input source (file / camera / RTSP)",
    )

    # Input source width and height. Necessary for camera but can be skipped for video and RTSP.
    parser.add_argument(
        "-d",
        "--input_dims",
        type=validate_inp_dims,
        metavar="WIDTHxHEIGHT",
        help="Input size (widthxheight)",
    )

    # The codec used to compress the input video. Required only for video and RTSP.
    parser.add_argument(
        "-c",
        "--input_codec",
        type=str,
        default="h264",
        help="Input codec for file/RTSP (default: %(default)s)",
    )

    # Whether to launch the demo in fullscreen
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        default=None,
        help="Launch demo in fullscreen",
    )

    inf_group = parser.add_argument_group("Inference parameters")

    # The path to the inference model to use. Must be a vaild SyNAP model with a ".synap" file extension.
    inf_group.add_argument(
        "-m", "--model", type=str, metavar="FILE", help="SyNAP model file location"
    )

    # How many frames to skip between sucessive inferences.
    # Increasing this number may result in better performance but can look worse visually.
    inf_group.add_argument(
        "-s",
        "--inference_skip",
        type=int,
        metavar="N_FRAMES",
        default=1,
        help="How many frames to skip between each inference (default: %(default)s)",
    )

    # Maximum number of inference results to display per frame
    inf_group.add_argument(
        "-n",
        "--num_inferences",
        type=int,
        metavar="N_RESULTS",
        default=5,
        help="Maximum number of detections returned per frame (default: %(default)s)",
    )

    # Confidence threshold: only detections with scores above this will be considered valid
    inf_group.add_argument(
        "-t",
        "--confidence_threshold",
        type=float,
        metavar="SCORE",
        default=0.5,
        help="Confidence threshold for inferences (default: %(default)s)",
    )

    # A file containing class labels for use with inference results. The default is labels from the COCO dataset.
    # Only used with suitable tasks like Object Detection and Instance Segmentation.
    inf_group.add_argument(
        "-l",
        "--labels",
        type=str,
        metavar="JSON",
        default="/usr/share/synap/models/object_detection/coco/info.json",
        help="JSON file containing class labels to use with inference results",
    )

    args = parser.parse_args()

    main(args)
