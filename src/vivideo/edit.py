import datetime
import srt

import os
from pathlib import Path
import argparse
import subprocess

from align import list_cuts

parser = argparse.ArgumentParser(description="Edit Media")

parser.add_argument("-media", "--input_media_file", help="Input file", required=True)
parser.add_argument("-srt", "--input_srt_file", help="Input SRT file", required=True)
parser.add_argument("-txt", "--input_txt_file", help="Edited transcription TXT file", required=True)
parser.add_argument("-m", "--margin", default=50, help="Buffer between utterences", type=int)
parser.add_argument("-f", "--fade_milliseconds", default=125, help="Fade In/Out Buffer between utterences", type=int)
parser.add_argument("-s", "--speed", default=1.0, help="Playback speed", type=int)
parser.add_argument("-o", "--output_file", default="output.mp4", help="Output media", type=str)

# Docs: https://ffmpeg.org/ffmpeg.html
parser.add_argument("-v", "--loglevel", help="FFMpeg loglevel option", default="16")

parser.add_argument(
    "-d",
    "--dry_run",
    help="Dry run",
    dest="dry_run",
    default=False,
    action=argparse.BooleanOptionalAction,
)
parser.add_argument(
    "-g",
    "--greedy",
    help="Greedily selects next word, so runs faster",
    dest="greedy",
    default=True,
    action=argparse.BooleanOptionalAction,
)


def media_edit():
    """
    Advanced media edit and trimming capable of
    re-ordering trimmed segments of original media
    """
    # # Local Testing
    # parser = argparse.ArgumentParser()
    # parser.set_defaults(input_media_file='tmp/demo1.mp4',
    #                     input_srt_file='tmp/demo1.wav.srt',
    #                     input_txt_file='tmp/demo1_edited.wav.txt',
    #                     margin=50,
    #                     fade=250,
    #                     speed=0.5,
    #                     loglevel='16',
    #                     crossfade=True,
    #                     dry_run=False,
    #                     output_file='tmp/demo1.test_edit.mp4')

    args = parser.parse_args()
    args.speed = min(2.0, max(0.5, args.speed))

    with open(args.input_srt_file, "r") as f:
        subtitles = list(srt.parse(f.read()))
    with open(args.input_txt_file, "r") as f:
        desired_transcription = f.read()

    margin = datetime.timedelta(milliseconds=args.margin)

    output_path = Path(args.output_file)
    segments = []
    cmds = []
    cuts = list_cuts(subtitles, desired_transcription=desired_transcription, margin=margin)
    fade_seconds = datetime.timedelta(milliseconds=args.fade_milliseconds).total_seconds()
    audio_video_filter = []

    for c, cut in enumerate(cuts):
        segment_path = output_path.with_stem(f"segment_{c}")

        if args.fade_milliseconds > 0:
            audio_video_filter = [
                # video Filter
                "-vf",
                ",".join(
                    [
                        f"fade=t=in:st={cut.start.total_seconds()}:d={fade_seconds}",
                        f"fade=t=out:st={cut.end.total_seconds()-fade_seconds}:d={fade_seconds}",
                        "setpts=N/FRAME_RATE/TB",
                    ]
                ),
                # # Audio Filter
                "-af",
                ",".join(
                    [
                        f"afade=t=in:st={cut.start.total_seconds()}:d={fade_seconds}",
                        f"afade=t=out:st={cut.end.total_seconds()-fade_seconds}:d={fade_seconds}",
                        "asetpts=N/SR/TB",
                    ]
                ),
            ]

        # Create List of Segment Trim w/ Fade Commands for FFMpeg
        cmd = (
            [
                "ffmpeg",
                # Input media file
                "-i",
                args.input_media_file,
                # Trim
                "-ss",
                f"{int(1000 * cut.start.total_seconds())}ms",
                "-to",
                f"{int(1000 * cut.end.total_seconds())}ms",
            ]
            + audio_video_filter
            + [
                # Overwrite output
                "-y",
                # Loglevel
                "-v",
                args.loglevel,
                str(segment_path),
            ]
        )
        cmds.append(cmd)

        # Create List of Segment Files Filter Options for FFMpeg Concat
        segments.append(segment_path)

    for i, cmd in enumerate(cmds):
        if args.dry_run:
            print(" ".join(cmd))
        else:
            print("Running command: %i" % i, " ".join(cmd))
            subprocess.run(cmd)

    if args.speed != 1.0:
        speed_args = [
            "-filter_complex",
            f"[0:v]setpts={1.0/args.speed}*PTS[v];[0:a]atempo={args.speed}[a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
        ]
    else:
        speed_args = []

    # Concat Segments
    list_path = output_path.with_stem("video_segments").with_suffix(".txt")
    cmd_concat = (
        [
            "ffmpeg",
            # Force Format
            "-f",
            "concat",
            "-safe",
            "0",
            # File of input media
            "-i",
            f"{str(list_path)}",
        ]
        + speed_args
        + [
            # Overwrite output
            "-y",
            # Loglevel
            "-v",
            args.loglevel,
            str(output_path),
        ]
    )

    if args.dry_run:
        print(" ".join(cmd_concat))
    else:
        with open(str(list_path), "w") as f:
            for seg in segments:
                f.write(f"file {str(seg.name)}\n")

        print("Running command: %i" % i, " ".join(cmd_concat))
        subprocess.run(cmd_concat)

        # Clean up
        print("Cleaning up intermediate files:")
        try:
            os.remove(str(list_path))
        except OSError:
            pass

        for seg in segments:
            try:
                print(f" - {str(seg)}")
                os.remove(str(seg.absolute()))
            except OSError:
                pass


if __name__ == "__main__":
    media_edit()
