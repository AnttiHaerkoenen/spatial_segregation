#!/usr/bin/env bash

cd slides
pandoc -s --mathml -i -t revealjs slides-hitu-2019.md -o slides-hitu-2019.html
cd ..