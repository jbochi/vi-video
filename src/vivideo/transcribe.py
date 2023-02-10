import argparse
from collections import namedtuple
from datetime import timedelta
from typing import List, Optional

from videogrep.transcribe import transcribe as videogrep_transcribe

WordAndSpan = namedtuple("WordSpan", ["confidence", "start", "end", "word"])


def get_transcription_dict(media_file: str, model_path: Optional[str] = None) -> dict:
    return videogrep_transcribe(media_file, model_path=model_path)


def transcribe(media_file: str, model_path: Optional[str] = None) -> List[WordAndSpan]:
    transciption_dict = get_transcription_dict(media_file, model_path=model_path)
    words_with_spans = [
        WordAndSpan(
            confidence=word["conf"],
            start=timedelta(seconds=word["start"]),
            end=timedelta(seconds=word["end"]),
            word=word["word"],
        )
        for piece in transciption_dict
        for word in piece["words"]
    ]
    return words_with_spans


def generate_text(transcription: dict):
    return "\n".join([piece["content"] for piece in transcription])


def transcribe_main():
    parser = argparse.ArgumentParser(description="Generate transcription text")
    parser.add_argument("-i", "--input_media", help="Input file", required=True)
    parser.add_argument("-m", "--model_path", help="Path for vosk model", default=None)
    parser.add_argument("-t", "--output_txt_file", help="Output transcription TXT file", required=True)

    args = parser.parse_args()
    transcription = get_transcription_dict(args.input_media, model_path=args.model_path)
    text = generate_text(transcription)
    with open(args.output_txt_file, "w") as f:
        f.write(text)

if __name__ == "__main__":
    transcribe_main()
