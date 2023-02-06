import datetime
import re

from typing import Generator

import argparse
import srt

parser = argparse.ArgumentParser(description="Generate compact text")

parser.add_argument("-i", "--input_srt_file", help="Input SRT file", required=True)
parser.add_argument("-o", "--output_txt_file", help="Output TXT file", required=True)
parser.add_argument(
    "-m",
    "--margin",
    help="Maximum time between utterences in same paragraph (in milliseconds)",
    default=100,
    type=int,
)


def generate_text(
    subtitles: Generator[srt.Subtitle, None, None], margin: datetime.timedelta
) -> str:
    last_end = datetime.timedelta()
    pieces = []
    for sub in subtitles:
        is_punctuation = re.search(r"^[.,:;!?]", sub.content)
        is_utterance = re.search(r"\w", sub.content)
        is_whitespace = re.search(r"^\s*$", sub.content)

        if pieces and sub.start - last_end > margin:
            pieces[-1] += "\n"
        if is_utterance:
            last_end = sub.end

        if pieces and (is_punctuation or pieces[-1].endswith("\n")):
            pieces[-1] = pieces[-1] + sub.content
        elif pieces or not is_whitespace:
            pieces.append(sub.content)

    if pieces:
        pieces[-1] += "\n"
    text = " ".join(pieces)
    return text


def main():
    args = parser.parse_args()
    with open(args.input_srt_file, "r") as f:
        subtitles = srt.parse(f.read())
    margin = datetime.timedelta(milliseconds=args.margin)
    text = generate_text(subtitles, margin=margin)
    with open(args.output_txt_file, "w") as f:
        f.write(text)


if __name__ == "__main__":
    main()
