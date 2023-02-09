import pytest
import srt

from vivideo.transcribe import transcribe


@pytest.fixture
def transcription():
    return transcribe("samples/jfk.wav")
