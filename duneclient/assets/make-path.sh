#!/bin/bash
convert $1.png -alpha extract -threshold 50% pgm:- | potrace -i -t 120 - --svg > $1.svg
