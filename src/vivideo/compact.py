import argparse
from typing import Optional

from vivideo.transcribe import get_transcription_dict

parser = argparse.ArgumentParser(description="Generate compact text")
parser.add_argument("-i", "--input_media", help="Input file", required=True)
parser.add_argument("-m", "--model_path", help="Path for vosk model", default=None)
parser.add_argument("-t", "--output_txt_file", help="Output transcription TXT file", required=True)


def generate_text(transcription: dict):
    return "\n".join([piece["content"] for piece in transcription])



if __name__ == "__main__":
    args = parser.parse_args()
    transcription = get_transcription_dict(args.input_media, model_path=args.model_path)
    text = generate_text(transcription)
    with open(args.output_txt_file, "w") as f:
        f.write(text)
