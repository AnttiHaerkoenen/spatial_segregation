#!/usr/bin/env bash

cd slides
pandoc -s --mathml -i -t revealjs slides-hitu-2019.md -o slides-hitu-2019.html
sed -i 's/font-size: 80px/font-size: 55px/g' slides-hitu-2019.html
cd ..