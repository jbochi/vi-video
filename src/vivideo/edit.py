import datetime

import argparse
import subprocess
import srt

from align import list_cuts

parser = argparse.ArgumentParser(description="Generate compact text")

parser.add_argument("-media", "--input_media_file", help="Input file", required=True)
parser.add_argument("-srt", "--input_srt_file", help="Input SRT file", required=True)
parser.add_argument(
    "-txt", "--input_txt_file", help="Edited transcription TXT file", required=True
)
parser.add_argument(
    "-m", "--margin", help="Buffer between utterences", default=50, type=int
)
parser.add_argument(
    "-o", "--output_file", help="Output media", default="output.mp4", type=str
)
parser.add_argument("-d", "--dry_run", help="Dry run", default=False, type=bool)
parser.add_argument(
    "-g",
    "--greedy",
    help="Greedily selects next word, so runs faster",
    default=True,
    type=bool,
    action=argparse.BooleanOptionalAction,
)


def main():
    args = parser.parse_args()
    with open(args.input_srt_file, "r") as f:
        subtitles = list(srt.parse(f.read()))
    with open(args.input_txt_file, "r") as f:
        desired_transcription = f.read()

    margin = datetime.timedelta(milliseconds=args.margin)
    cuts = list_cuts(
        subtitles,
        desired_transcription=desired_transcription,
        margin=margin,
        greedy=args.greedy,
    )

    between = "+".join(
        f"between(t,{cut.start.total_seconds()},{cut.end.total_seconds()})"
        for cut in cuts
    )
    cmd = [
        "ffmpeg",
        "-i",
        args.input_media_file,
        "-vf",
        f"select='{between}',setpts=N/FRAME_RATE/TB",
        "-af",
        f"aselect='{between}',asetpts=N/SR/TB",
        args.output_file,
    ]
    if args.dry_run:
        print(" ".join(cmd))
    else:
        print("Running command: ", " ".join(cmd))
        subprocess.run(cmd)


if __name__ == "__main__":
    main()
