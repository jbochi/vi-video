import argparse

from vivideo.transcribe import get_transcription_dict

parser = argparse.ArgumentParser(description="Generate compact text")
parser.add_argument("-i", "--input_media", help="Input file", required=True)
parser.add_argument("-m", "--model_path", help="Path for vosk model", default=None)
parser.add_argument("-t", "--output_txt_file", help="Output transcription TXT file", required=True)


def generate_text(input_media, model_path, output_txt_file):
    transcription = get_transcription_dict(input_media, model_path=model_path)
    text = "\n".join([piece["content"] for piece in transcription])
    with open(output_txt_file, "w") as f:
        f.write(text)


if __name__ == "__main__":
    args = parser.parse_args()
    generate_text(args.input_media, args.model_path, args.output_txt_file)
