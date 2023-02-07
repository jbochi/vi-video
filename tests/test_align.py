from datetime import timedelta

import pytest
import srt

from vivideo.align import Cut, list_cuts


def test_list_cuts(subtitles):
    desired_transcription = "your country can do for your country"
    cuts = list_cuts(
        list(subtitles),
        desired_transcription,
        margin=timedelta(milliseconds=50),
    )
    expected = [
        Cut(
            start=timedelta(seconds=5, microseconds=360000),
            end=timedelta(seconds=7, microseconds=60000),
        ),
        Cut(
            start=timedelta(seconds=9, microseconds=710000),
            end=timedelta(seconds=10, microseconds=560000),
        ),
    ]
    assert cuts == expected


def test_list_cuts_accepts_apostrophes():
    subtitles = srt.parse(
        """1
00:00:00,000 --> 00:00:01,000
I

2
00:00:01,000 --> 00:00:02,000
'm

3
00:00:02,000 --> 00:00:03,000
a

4
00:00:03,000 --> 00:00:04,000
subtitle

5
00:00:04,000 --> 00:00:05,000
."""
    )

    desired_transcription = "I 'm"

    cuts = list_cuts(
        list(subtitles),
        desired_transcription,
        margin=timedelta(milliseconds=0),
    )
    expected = [
        Cut(
            start=timedelta(seconds=0),
            end=timedelta(seconds=2),
        ),
    ]
    assert cuts == expected


@pytest.mark.skip("TODO: fix this, it should work")
def test_list_cuts_allows_pieces_to_be_merged_without_space():
    subtitles = srt.parse(
        """1
00:00:00,000 --> 00:00:01,000
I

2
00:00:01,000 --> 00:00:02,000
'm

3
00:00:02,000 --> 00:00:03,000
dumb."""
    )

    desired_transcription = "I'm"

    cuts = list_cuts(
        list(subtitles),
        desired_transcription,
        margin=timedelta(milliseconds=0),
    )
    expected = [
        Cut(
            start=timedelta(seconds=0),
            end=timedelta(seconds=2),
        ),
    ]
    assert cuts == expected


def test_allows_transposition():
    subtitles = srt.parse(
        """1
00:00:00,000 --> 00:00:01,000
first

2
00:00:01,000 --> 00:00:02,000
second

3
00:00:02,000 --> 00:00:03,000
third"""
    )

    desired_transcription = "first third second"

    cuts = list_cuts(
        list(subtitles),
        desired_transcription,
        margin=timedelta(milliseconds=0),
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
    subtitles = srt.parse(
        """1
00:00:00,000 --> 00:00:01,000
I

2
00:00:01,000 --> 00:00:02,000
I

2
00:00:02,000 --> 00:00:03,000
like

3
00:00:03,000 --> 00:00:04,000
this"""
    )

    desired_transcription = "I like this"

    cuts = list_cuts(
        list(subtitles),
        desired_transcription,
        margin=timedelta(milliseconds=0),
    )
    expected = [
        Cut(
            start=timedelta(seconds=1),
            end=timedelta(seconds=4),
        )
    ]
    assert cuts == expected


def test_does_not_minimize_cuts_in_greed_mode():
    subtitles = srt.parse(
        """1
00:00:00,000 --> 00:00:01,000
I

2
00:00:01,000 --> 00:00:02,000
I

2
00:00:02,000 --> 00:00:03,000
like

3
00:00:03,000 --> 00:00:04,000
this"""
    )

    desired_transcription = "I like this"

    cuts = list_cuts(
        list(subtitles),
        desired_transcription,
        margin=timedelta(milliseconds=0),
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
