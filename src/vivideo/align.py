import datetime
import re

from typing import Generator, List, Tuple

from collections import namedtuple
import argparse
import srt

parser = argparse.ArgumentParser(description="Generate compact text")

parser.add_argument("-srt", "--input_srt_file", help="Input SRT file", required=True)
parser.add_argument(
    "-txt", "--input_txt_file", help="Edited transcription TXT file", required=True
)
parser.add_argument(
    "-m", "--margin", help="Buffer between utterences", default=50, type=int
)

Cut = namedtuple("Cut", ["start", "end"])


def pick_segments(
    subtitles: List[srt.Subtitle],
    desired_transcription: str,
) -> List[Cut]:
    """Gitven a list of subtitles and a desired transcription, return a list of cuts
    (start, end) that correspond to segments of the media with the desired transcription.
    """
    # TODO: Should minimize number of cuts and allow transposition of words.
    subtitle_index = 0
    n_subtitles = len(subtitles)
    output = []
    for word in re.findall(r"\w+", desired_transcription):
        while (
            subtitle_index < n_subtitles
            and subtitles[subtitle_index].content.lower() != word.lower()
        ):
            subtitle_index += 1
        if subtitle_index == n_subtitles:
            raise ValueError(
                f"Could not find all words in subtitles. First missing word: {word}"
            )
        output.append(
            Cut(subtitles[subtitle_index].start, subtitles[subtitle_index].end)
        )
        subtitle_index += 1
    return output


def merge_segments(cut: List[Cut], margin: datetime.timedelta) -> List[Cut]:
    """Given a list of cuts, merge cuts that are within margin of each other."""
    # TODO: should decrease margin to avoid including undesired words.
    output = []
    for start, end in cut:
        start -= margin
        end += margin
        if start < datetime.timedelta():
            start = datetime.timedelta()
        if output and output[-1].end > start:
            output[-1] = Cut(output[-1].start, end)
        else:
            output.append(Cut(start, end))
    return output


def list_cuts(
    subtitles: List[srt.Subtitle],
    desired_transcription: str,
    margin: datetime.timedelta,
) -> List[Cut]:
    """Gitven a list of subtitles and a desired transcription, return a list of cuts
    (start, end) that correspond to segments of the media with the desired transcription. Also
    includes a configurable margin of time before and after each cut."""
    segments = pick_segments(subtitles, desired_transcription)
    return merge_segments(segments, margin)


def main():
    args = parser.parse_args()
    with open(args.input_srt_file, "r") as f:
        subtitles = list(srt.parse(f.read()))
    with open(args.input_txt_file, "r") as f:
        desired_transcription = f.read()

    margin = datetime.timedelta(milliseconds=args.margin)
    print(
        list_cuts(subtitles, desired_transcription=desired_transcription, margin=margin)
    )


if __name__ == "__main__":
    main()
