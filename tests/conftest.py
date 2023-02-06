import pytest
import srt


@pytest.fixture
def subtitles():
    with open("samples/jfk.wav.srt", "r") as f:
        return srt.parse(f.read())
