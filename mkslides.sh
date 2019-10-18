#!/usr/bin/env bash

cd slides
pandoc -s --mathml -i -t revealjs slides-hitu-2019.md -o slides-hitu-2019.html --include-in-header custom.css
sed 's/black.css/sky.css/g' slides-hitu-2019.html -i slides-hitu-2019.html
sed 's///g' slides-hitu-2019.html -i slides-hitu-2019.html
cd ..