#!/usr/bin/env bash

cd slides
pandoc -s --mathml -i -t dzslides slides-2019-10-07.md -o slides-2019-10-07.html
cd ..