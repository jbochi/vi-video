from datetime import timedelta

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
        margin=timedelta(milliseconds=00),
    )
    expected = [
        Cut(
            start=timedelta(seconds=0),
            end=timedelta(seconds=1),
        ),
        Cut(
            start=timedelta(seconds=1),
            end=timedelta(seconds=2),
        ),
    ]
    assert cuts == expected
