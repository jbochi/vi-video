#!/bin/zsh
# $1:source1 $2:source12 $3:destination
usage="Usage: concat <input media1> <input media2> <output media> \n"
usage+=' ffmpeg -i "$1" -i "$2" -filter_complex "[0:v] [0:a] [1:v] [1:a] concat=n=2:v=1:a=1 [v] [a]" -map "[v]" -map "[a]" "$3"'
[[ -z $1 || $1 = -h || $1 = --help ]] &&
echo $usage && return 0
[[ ! -f $1 ]] &&
echo -e "$usage\nSource video not a file: '$1'" && return 1
[[ ! -f $2 ]] &&
echo -e "$usage\nSource video not a file: '$2'" && return 1

# ffmpeg -f concat -i "$1" -c:v copy -c:a aac "$2" (Can misalign audio/video)
ffmpeg -i "$1" -i "$2" -filter_complex "[0:v] [0:a] [1:v] [1:a] concat=n=2:v=1:a=1 [v] [a]" -map "[v]" -map "[a]" "$3"