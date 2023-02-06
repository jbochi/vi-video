import datetime

from vivideo import compact

def test_generate_text():
    expected = 'And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.\n'
    text = compact.generate_text('samples/jfk.wav.srt', margin=datetime.timedelta(milliseconds=1000))
    assert text == expected


def test_generate_text_with_short_margin():
    expected = 'And so my fellow Americans,\nask not what your country can do for you, ask what you can do for your country.\n'
    text = compact.generate_text('samples/jfk.wav.srt', margin=datetime.timedelta(milliseconds=100))
    assert text == expected
