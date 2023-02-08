#!/bin/zsh
# $1:source $2:destination
usage="Usage: convert2wav <input media> <output media> \n"
usage+=" ffmpeg -i <input media> -ac 1 -ar 16000 -c:a pcm_s16le <output media>"
[[ -z $1 || $1 = -h || $1 = --help ]] &&
echo $usage && return 0
[[ ! -f $1 ]] &&
echo -e "$usage\nSource video not a file: '$1'" && return 1
ffmpeg -i "$1" -ac 1 -ar 16000 -c:a pcm_s16le "$2"
