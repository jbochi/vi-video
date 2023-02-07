import datetime
from pathlib import Path

import argparse
import subprocess
import srt

from align import list_cuts

parser = argparse.ArgumentParser(description="Edit Media")

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

parser.add_argument(
    "-f", "--fade", help="Fade In/Out Buffer between utterences", default=75, type=int
    )

# Python 3.9+ Supports parser.add_argument("--foo", action=argparse.BooleanOptionalAction)
parser.add_argument("-xf", "--crossfade",  help="Media segments cross-fading", 
                        dest='crossfade', default=False, action='store_true')
parser.add_argument("-d", "--dry_run", help="Dry run", 
                        dest='dry_run',  default=False, action='store_true')
parser.add_argument(
    "-g",
    "--greedy",
    help="Greedily selects next word, so runs faster",
    dest='greedy',
    default=True,
    action='store_true'
    # action=argparse.BooleanOptionalAction,
)


def media_edit():
    """
    Advanced media edit and trimming capable of re-ordering trimmed segments of original media
    """
    parser = argparse.ArgumentParser()
    parser.set_defaults(input_media_file='tmp/demo1.mp4', 
                        input_srt_file='tmp/demo1.wav.srt', 
                        input_txt_file='tmp/demo1_edited.wav.txt',
                        margin=50,
                        fade=250,
                        crossfade=True,
                        dry_run=False,
                        output_file='tmp/demo1.edited.mp4')
    args = parser.parse_args()

    with open(args.input_srt_file, "r") as f:
        subtitles = list(srt.parse(f.read()))
    with open(args.input_txt_file, "r") as f:
        desired_transcription = f.read()

    margin = datetime.timedelta(milliseconds=args.margin)
    crossfade = datetime.timedelta(milliseconds=args.fade if args.crossfade else 0)

    output_path = Path(args.output_file)
    segments = []
    cmds = []
    cuts = list_cuts(
        subtitles, desired_transcription=desired_transcription, margin=margin
    )

    for c, cut in enumerate(cuts):
        segment_path = output_path.with_stem(f'segment_{c}')
        between = f"between(t,{cut.start.total_seconds()},{cut.end.total_seconds()})"

        # Create List of Segment Trim w/ Fade Commands for FFMpeg
        # ffmpeg -i tmp/demo1.mp4 -ss 1.14 -to 3.82 
        #           -vf fade=t=in:st=1:14:d=0.75,fade=t=out:st=3:81:d=0.75 
        #           -af afade=t=in:st=1.14:d=0.75,afade=t=out:st=3:81:d=0.75  tmp/segment_0.mp4
        cmd = [
            "ffmpeg",
            
            "-i",
            args.input_media_file,

            f"-ss {cut.start.total_seconds()} -to {cut.end.total_seconds()}",

            "-vf",
            ','.join([
                f"fade=t=in:st={cut.start.total_seconds()}:d={crossfade.total_seconds()}",
                f"fade=t=out:st={cut.end.total_seconds()-crossfade.total_seconds()}:d={crossfade.total_seconds()}",
                "setpts=N/FRAME_RATE/TB"
                ]),

            "-af",
            ','.join([
                f"afade=t=in:st={cut.start.total_seconds()}:d={crossfade.total_seconds()}", 
                f"afade=t=out:st={cut.end.total_seconds()-crossfade.total_seconds()}:d={crossfade.total_seconds()}",
                "asetpts=N/SR/TB"
                ]),

            str(segment_path)
        ]
        cmds.append(cmd)

        # Create List of Segment Files Filter Options for FFMpeg Concat
        segments.append(f'{str(segment_path)}')


    for i, cmd in enumerate(cmds):
        if args.dry_run:
                print(" ".join(cmd))
        else:
            print("Running command: %i" %i, " ".join(cmd))
            subprocess.run(cmd)

    # Concat Segments
    list_path = output_path.with_stem('video_segments').with_suffix('.txt')
    cmd_concat = ["ffmpeg", 
            "-f concat", 
            # "-safe 0", 
            f"-i {str(list_path)}",
            "-c copy",
             str(output_path)]

    if args.dry_run:
        print(" ".join(cmd_concat))
    else:
        with open(str(list_path), 'w') as f:
            for seg in segments:
                f.write(f"file {seg}\n")

        print("Running command: %i" %i, " ".join(cmd_concat))
        subprocess.run(cmd_concat)



# def media_edit_ordered():
#     """
#     Simple media edit and trimming with ordered timelines only
#     """
#     args = parser.parse_args()
#     with open(args.input_srt_file, "r") as f:
#         subtitles = list(srt.parse(f.read()))
#     with open(args.input_txt_file, "r") as f:
#         desired_transcription = f.read()

#     margin = datetime.timedelta(milliseconds=args.margin)
#     cuts = list_cuts(
#         subtitles,
#         desired_transcription=desired_transcription,
#         margin=margin,
#         greedy=args.greedy,
#     )

#     between = "+".join(
#         f"between(t,{cut.start.total_seconds()},{cut.end.total_seconds()})"
#         for cut in cuts
#     )
#     cmd = [
#         "ffmpeg",
#         "-i",
#         args.input_media_file,
#         "-vf",
#         f"select='{between}',setpts=N/FRAME_RATE/TB",
#         "-af",
#         f"aselect='{between}',asetpts=N/SR/TB",
#         args.output_file,
#     ]
#     if args.dry_run:
#         print(" ".join(cmd))
#     else:
#         print("Running command: ", " ".join(cmd))
#         subprocess.run(cmd)


if __name__ == "__main__":

    media_edit()
