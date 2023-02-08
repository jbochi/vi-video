#!/bin/zsh
# $1:source1 $2:source2 $3:destination
usage="Usage: blend <input media1>  <input media2> <output media> \n"
usage+=" ffmpeg -i <input media1> -i <input media2> -c:v copy -c:a aac  <output media>"
[[ -z $1 || $1 = -h || $1 = --help ]] &&
echo $usage && return 0
[[ ! -f $1 ]] &&
echo -e "$usage\nSource video not a file: '$1'" && return 1
[[ ! -f $2 ]] &&
echo -e "$usage\nSource video not a file: '$1'" && return 1
ffmpeg -i "$1" -i "$2" -c:v copy -c:a aac "$3"
