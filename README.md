# vi-video

Edit videos with vi or your favorite text editor.

## Overview

Editing a video or audio file with this tool consists of three steps:

- Run one command to transcribe the media you want to edit
- Edit the text transcription file in `vi` or your favorite text editor
- Run another command to cut the video

### Example commands

To install this package, run:

```console
pip install vivideo
```

To generate a trascription text file, you can run this command:

```console
vivideo-transcribe -i samples/jfk.wav -t samples/jfk.txt
```

After you have edited the transcription (we recommend you save it with another name), run something like this:

```console
vivideo-edit -i samples/jfk.wav -t samples/jfk.edited.txt -o samples/jfk.edited.wav --no-greedy
```

 Vi-Video uses [FFMpeg](https://ffmpeg.org/) as audio and video processing tools. In order to execute the steps above, it is required to have FFMpeg library installed ([read more](./docs/ffmpeg.MD)).

 You will also need to run `pip install vosk` to generate the transcriptions.

## Algorithm

MVP aligns each word in the desired transcript to its first occurrance in the original transcription. It only looks for matches that occur after the last matched word/timestamp, so transpositions are not allowed.

To make the result seem nicer, it will include a margin before and after each cut, as in [auto-editor](https://valle-demo.github.io/). If the margin of one cut would overlap with the margin of the following cut, then we don't make a cut.

We will probably want to use something like [Damerau–Levenshtein distance](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance) to find the best possible alignment between original string (transcription) and desired output string (edited script).

If the desired transcript contains words not in the original (inclusions), we could do overdub or speech synthesis with something like [VALL-E](https://valle-demo.github.io/).

## Alternatives

This is the poor man's version of [descript](https://www.descript.com/tour), which allows you to edit
a video like it's a text document.

The best open source tool we could find that do something similar to this are [auto-editor](https://github.com/WyattBlue/auto-editor) and [videogrep](https://github.com/antiboredom/videogrep)
