import argparse
import re
import json
from collections import namedtuple
from datetime import timedelta
from typing import List, Optional
from pathlib import Path
import subprocess

from vosk import Model, KaldiRecognizer, SetLogLevel
from videogrep.transcribe import transcribe as videogrep_transcribe
import imageio_ffmpeg

MAX_CHARS = 36
WordAndSpan = namedtuple("WordSpan", ["confidence", "start", "end", "word"])


def get_transcription_dict_grammar(
    videofile: str,
    grammar: List[str] = None,
    model_path: Optional[str] = None,
    model_name: Optional[str] = None,
) -> List[dict]:
    """
    Transcribes a video file using Vosk models
        vosk-model-small-en-us-0.15
        vosk-model-en-us-0.22
        vosk-model-en-us-0.22-lgraph
        vosk-model-en-us-0.42-gigaspeech

    :param videofile str: Video file path
    :param grammar list[str]: Optional list of vocablary
    :param model_path str: Optional vosk model folder
    :param model_name str: Optional vosk model name
    :rtype List[dict]: A list of timestamps and content
    """

    transcript_file = Path(videofile).with_suffix(".json")

    if Path(transcript_file).exists():
        with open(transcript_file, "r") as infile:
            data = json.load(infile)
        return data

    if Path(transcript_file).exists():
        print("Could not find file", videofile)
        return []

    if model_path is None:
        if model_name is None:
            print("No model is identified. Using default US English model")
            model = Model(lang="en-us")
        else:
            model = Model(model_name=model_name)
    elif Path(model_path).exists():
        model = Model(model_path)
    else:
        print("Could not find model folder")
        exit(1)

    print("Transcribing", videofile)
    SetLogLevel(0)
    sample_rate = 16000
    rec = KaldiRecognizer(model, sample_rate, str(grammar))
    rec.SetWords(True)

    process = subprocess.Popen(
        [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-nostdin",
            "-loglevel",
            "quiet",
            "-i",
            videofile,
            "-ar",
            str(sample_rate),
            "-ac",
            "1",
            "-f",
            "s16le",
            "-",
        ],
        stdout=subprocess.PIPE,
    )

    tot_samples = 0
    result = []
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            tot_samples += len(data)
            rec.SetGrammar(grammar)
            result.append(json.loads(rec.Result()))
        # else:
        #     result.append(json.loads(rec.PartialResult()))

    result.append(json.loads(rec.FinalResult()))

    out = []
    for r in result:
        if "result" not in r:
            continue
        words = [w for w in r["result"]]
        item = {"content": "", "start": None, "end": None, "words": []}
        for w in words:
            item["content"] += w["word"] + " "
            item["words"].append(w)
            if len(item["content"]) > MAX_CHARS or w == words[-1]:
                item["content"] = item["content"].strip()
                item["start"] = item["words"][0]["start"]
                item["end"] = item["words"][-1]["end"]
                out.append(item)
                item = {"content": "", "start": None, "end": None, "words": []}

    if len(out) == 0:
        print("No words found in", videofile)
        return []

    with open(transcript_file, "w", encoding="utf-8") as outfile:
        json.dump(out, outfile)

    return out


def transcribe(
    media_file: str, model_path: Optional[str] = None, model_name: Optional[str] = None
) -> List[WordAndSpan]:
    transciption_dict = get_transcription_dict(media_file, model_path=model_path, model_name=model_name)
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


def get_transcription_dict(
    media_file: str,
    grammar_file: Optional[str] = None,
    model_path: Optional[str] = None,
    model_name: Optional[str] = None,
) -> dict:
    if grammar_file is None:
        return videogrep_transcribe(media_file, model_path=model_path)
    else:
        # Read Grammar [1 Word per Line] and set Grammar as List of Strings
        try:
            with open(grammar_file, "r") as gfile:
                grammar = gfile.readlines()
                grammar = [re.sub("\n", "", w).lower() for w in grammar]
        except IOError:
            print("grammar file not found ", grammar_file)
            exit(1)

        return get_transcription_dict_grammar(
            media_file, grammar=grammar, model_path=model_path, model_name=model_name
        )


def generate_text(transcription: dict):
    return "\n".join([piece["content"] for piece in transcription])


def transcribe_main():
    parser = argparse.ArgumentParser(description="Generate transcription text")
    parser.add_argument("-i", "--input_media", help="Input file", required=True)
    parser.add_argument("-t", "--output_txt_file", help="Output transcription TXT file", required=True)
    parser.add_argument("-m", "--model_path", help="Path for vosk model", default=None)
    parser.add_argument("-n", "--model_name", help="Name for vosk model", default=None)
    parser.add_argument("-g", "--grammar_file", help="Updating recognizer vocabulary in runtime", default=None)

    args = parser.parse_args()
    transcription = get_transcription_dict(
        args.input_media, grammar_file=args.grammar_file, model_path=args.model_path, model_name=args.model_name
    )
    if transcription:
        text = generate_text(transcription)
        with open(args.output_txt_file, "w") as f:
            f.write(text)


if __name__ == "__main__":
    transcribe_main()
