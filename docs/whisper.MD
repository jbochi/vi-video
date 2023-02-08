# Whisper

[Whisper.CPP](https://github.com/ggerganov/whisper.cpp) is recommended for transcripting the media/audio files.


Different sizes of whisper model can be downloaded and used ([read more](https://github.com/ggerganov/whisper.cpp#more-audio-samples))
```console
bash ./models/download-ggml-model.sh medium.en
bash ./models/download-ggml-model.sh large
```
Specific size of whisper model can be deployed to transcribe a media file:
```console
./main -m ./models/ggml-medium.en.bin -f <infile_wav> -osrt -ml 1
./main -m ./models/ggml-medium.en.bin -f <infile_wav> -otxt 
```