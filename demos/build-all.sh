#!/bin/bash

set -e -x

for demofile in ./demos/*.exp; do
    name="${demofile##*/}"
    name="${name//.exp/}"
    asciinema rec --overwrite \
        --rows 25 --cols 100 \
        -c "$demofile" "demos/${name}.cast"
    agg \
        --speed 3 \
        --theme asciinema \
        "demos/${name}.cast" "demos/${name}.gif"
done
