#!/usr/bin/env bash

cd slides
pandoc -s --mathml -i -t dzslides slides-2019-10-07.md -o slides-2019-10-07.html
sed -i 's/font-size: 80px/font-size: 55px/g' slides-2019-10-07.html
cd ..