from datetime import timedelta

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
