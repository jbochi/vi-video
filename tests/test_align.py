from datetime import timedelta

import pytest
import srt

from vivideo.align import Cut, list_cuts
from vivideo.transcribe import WordAndSpan


def test_list_cuts(transcription):
    desired_transcription = "your country can do for your country"
    cuts = list_cuts(
        transcription,
        desired_transcription,
        padding=timedelta(milliseconds=50),
    )
    expected = [
        Cut(
            start=timedelta(seconds=5, microseconds=560000),
            end=timedelta(seconds=6, microseconds=500000),
        ),
        Cut(
            start=timedelta(seconds=9, microseconds=160000),
            end=timedelta(seconds=10, microseconds=550000),
        ),
    ]
    assert cuts == expected


def test_list_cuts_accepts_apostrophes():
    transcription = [
        WordAndSpan(word="I'm", confidence=1, start=timedelta(seconds=0), end=timedelta(seconds=2)),
        WordAndSpan(word="a", confidence=1, start=timedelta(seconds=2), end=timedelta(seconds=3)),
        WordAndSpan(word="subtitle", confidence=1, start=timedelta(seconds=3), end=timedelta(seconds=4)),
    ]

    desired_transcription = "I'm"

    cuts = list_cuts(
        transcription,
        desired_transcription,
        padding=timedelta(milliseconds=0),
    )
    expected = [
        Cut(
            start=timedelta(seconds=0),
            end=timedelta(seconds=2),
        ),
    ]
    assert cuts == expected


def test_allows_transposition():
    transcription = [
        WordAndSpan(word="first", confidence=1, start=timedelta(seconds=0), end=timedelta(seconds=1)),
        WordAndSpan(word="second", confidence=1, start=timedelta(seconds=1), end=timedelta(seconds=2)),
        WordAndSpan(word="third", confidence=1, start=timedelta(seconds=2), end=timedelta(seconds=3)),
    ]

    desired_transcription = "first third second"

    cuts = list_cuts(
        transcription,
        desired_transcription,
        padding=timedelta(milliseconds=0),
    )
    expected = [
        Cut(
            start=timedelta(seconds=0),
            end=timedelta(seconds=1),
        ),
        Cut(
            start=timedelta(seconds=2),
            end=timedelta(seconds=3),
        ),
        Cut(
            start=timedelta(seconds=1),
            end=timedelta(seconds=2),
        ),
    ]
    assert cuts == expected


def test_minimize_cuts():
    transcription = [
        WordAndSpan(word="I", confidence=1, start=timedelta(seconds=0), end=timedelta(seconds=1)),
        WordAndSpan(word="I", confidence=1, start=timedelta(seconds=1), end=timedelta(seconds=2)),
        WordAndSpan(word="like", confidence=1, start=timedelta(seconds=2), end=timedelta(seconds=3)),
        WordAndSpan(word="this", confidence=1, start=timedelta(seconds=3), end=timedelta(seconds=4)),
    ]

    desired_transcription = "I like this"

    cuts = list_cuts(
        transcription,
        desired_transcription,
        padding=timedelta(milliseconds=0),
    )
    expected = [
        Cut(
            start=timedelta(seconds=1),
            end=timedelta(seconds=4),
        )
    ]
    assert cuts == expected


def test_does_not_minimize_cuts_in_greed_mode():
    transcription = [
        WordAndSpan(word="I", confidence=1, start=timedelta(seconds=0), end=timedelta(seconds=1)),
        WordAndSpan(word="I", confidence=1, start=timedelta(seconds=1), end=timedelta(seconds=2)),
        WordAndSpan(word="like", confidence=1, start=timedelta(seconds=2), end=timedelta(seconds=3)),
        WordAndSpan(word="this", confidence=1, start=timedelta(seconds=3), end=timedelta(seconds=4)),
    ]


    desired_transcription = "I like this"

    cuts = list_cuts(
        transcription,
        desired_transcription,
        padding=timedelta(milliseconds=0),
        greedy=True,
    )
    expected = [
        Cut(
            start=timedelta(seconds=0),
            end=timedelta(seconds=1),
        ),
        Cut(
            start=timedelta(seconds=2),
            end=timedelta(seconds=4),
        ),
    ]
    assert cuts == expected
