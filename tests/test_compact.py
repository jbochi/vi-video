import datetime

import pytest
import srt

from vivideo import compact


@pytest.fixture
def subtitles():
    with open("samples/jfk.wav.srt", "r") as f:
        return srt.parse(f.read())


def test_generate_text(subtitles):
    expected = (
        "And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.\n"
    )
    text = compact.generate_text(subtitles, margin=datetime.timedelta(milliseconds=1000))
    assert text == expected


def test_generate_text_with_short_margin(subtitles):
    expected = "And so my fellow Americans,\nask not what your country can do for you, ask what you can do for your country.\n"
    text = compact.generate_text(subtitles, margin=datetime.timedelta(milliseconds=100))
    assert text == expected
