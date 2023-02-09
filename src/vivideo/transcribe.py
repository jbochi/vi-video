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
