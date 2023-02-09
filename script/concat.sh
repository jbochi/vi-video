#!/bin/zsh
# $1:source1 $3:destination
usage="Usage: concat <input list> <output media> \n"
usage+=" ffmpeg -i <input list> -c:v copy -c:a aac  <output media> \n"
usage+=" <input list> Line format: file  <name.ext>"
[[ -z $1 || $1 = -h || $1 = --help ]] &&
echo $usage && return 0
[[ ! -f $1 ]] &&
echo -e "$usage\nSource video not a file: '$1'" && return 1
ffmpeg -f concat -safe 0 -i "$1" -c:v copy -c:a aac "$2"
