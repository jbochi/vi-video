import pytest

from vivideo.transcribe import get_transcription_dict, generate_text


@pytest.fixture
def transcription_dict():
    return get_transcription_dict("samples/jfk.wav")


def test_generate_text(transcription_dict):
    expected = """and so my fellow americans ask not what\nyour country can do for you ask what
you can do for your country"""
    text = generate_text(transcription_dict)
    assert text == expected
