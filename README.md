# vi-video

Edit videos with vi or your favorite text editor.

## Overview

Editing a video or audio file with this tool consists of three steps:

- Create a srt file and a text file with the transcription
- Edit the text transcription file
- Run this tool

Execution looks like this:

```console
python src/vivideo/edit.py -media samples/jfk.wav -srt samples/jfk.wav.srt -txt samples/jfk.wav.edited.txt -o samples/jfk.edited.wav
```

If you want to debug which segments of the video are going to be preserved, you can run something like this:

```console
python src/vivideo/align.py -srt samples/jfk.wav.srt -txt samples/jfk.wav.edited.txt
```

 Vi-Video uses [FFMpeg](https://ffmpeg.org/) as audio and video processing tools. In order to execute the steps above, it is required to have FFMpeg library installed ([read more](./docs/ffmpeg.MD)). 

## Creating srt files and text script files

We suggest [whisper.cpp](https://github.com/ggerganov/whisper.cpp) to generate srt files with the
transcription of the file you want to edit. Use `--max-len 1` for word-level timestamps.

```console
./main -m models/ggml-base.en.bin -f samples/jfk.wav  --output-srt --output-txt  --max-len 1
```

To generate the trascription text file, you can run this command:

```console
python src/vivideo/compact.py -i samples/jfk.wav.srt -o samples/jfk.wav.txt
```

## Algorithm

MVP aligns each word in the desired transcript to its first occurrance in the original transcription. It only looks for matches that occur after the last matched word/timestamp, so transpositions are not allowed.

To make the result seem nicer, it will include a margin before and after each cut, as in [auto-editor](https://valle-demo.github.io/). If the margin of one cut would overlap with the margin of the following cut, then we don't make a cut.

We will probably want to use something like [Damerau–Levenshtein distance](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance) to find the best possible alignment between original string (transcription) and desired output string (edited script).

If the desired transcript contains words not in the original (inclusions), we could do overdub or speech synthesis with something like [VALL-E](https://valle-demo.github.io/).

## Alternatives

This is the poor man's version of [descript](https://www.descript.com/tour), which allows you to edit
a video like it's a text document.

The best open source tool we could find is [auto-editor](https://github.com/WyattBlue/auto-editor).
