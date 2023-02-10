import argparse
import datetime
import os
import subprocess
from pathlib import Path

from videogrep.videogrep import create_supercut_in_batches

from vivideo.align import list_cuts
from vivideo.transcribe import transcribe

parser = argparse.ArgumentParser(description="Edit Media")

parser.add_argument("-i", "--input_media_file", help="Input file", required=True)
parser.add_argument("-t", "--desired_transcription_file", help="Edited transcription TXT file", required=True)
parser.add_argument("-p", "--padding", default=10, help="Buffer between utterences in milliseconds", type=int)
parser.add_argument("-f", "--fade_ms", default=0, help="Fade In/Out Buffer between utterences", type=int)
parser.add_argument("-s", "--speed", default=1.0, help="Playback speed", type=int)
parser.add_argument("-o", "--output_file", default="output.mp4", help="Output media", type=str)
parser.add_argument(
    "-v", "--loglevel", help="FFMpeg loglevel option. Refer to https://ffmpeg.org/ffmpeg.html", default="16"
)
parser.add_argument("-m", "--model_path", help="Path for vosk model", default=None)
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


def edit_main():
    """
    Advanced media edit and trimming capable of
    re-ordering trimmed segments of original media
    """
    args = parser.parse_args()

    with open(args.desired_transcription_file, "r") as f:
        desired_transcription = f.read()
    transcription = transcribe(args.input_media_file, model_path=args.model_path)

    padding = datetime.timedelta(milliseconds=args.padding)
    cuts = list_cuts(transcription, desired_transcription=desired_transcription, padding=padding, greedy=args.greedy)
    print(f"Found {len(cuts)} cuts")
    if args.dry_run:
        for i, cut in enumerate(cuts):
            print(f"{i}: {cut.start} - {cut.end}")

    if args.speed == 1.0 and args.fade_ms == 0 and (not args.input_media_file.endswith(".wav")):
        cut_with_videogrep(args, cuts)
    else:
        cut_with_ffmpeg(args, cuts)


def cut_with_videogrep(args, cuts):
    if args.dry_run:
        return
    composition = [
        {"start": cut.start.total_seconds(), "end": cut.end.total_seconds(), "file": args.input_media_file}
        for cut in cuts
    ]
    create_supercut_in_batches(composition, args.output_file)


def cut_with_ffmpeg(args, cuts):
    output_path = Path(args.output_file)
    segments = []
    cmds = []

    fade_seconds = datetime.timedelta(milliseconds=args.fade_ms).total_seconds()
    audio_video_filter = []

    for c, cut in enumerate(cuts):
        segment_path = output_path.with_stem(f"segment_{c}")

        if args.fade_ms > 0:
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
    edit_main()
