#!/usr/bin/env bash

cd slides
pandoc -s --mathml -i -t dzslides slides-2019-10-07.md -o slides-2019-10-07.html
sed -i 's/font-size: 80px/font-size: 55px/g' slides-2019-10-07.html
convert orthodox_1880.png -resize 10% orthodox_1880.jpg
convert total_1880.png -resize 50% total_1880.jpg
convert orthodox_1900.png -resize 50% orthodox_1900.jpg
convert total_1900.png -resize 50% total_1900.jpg
convert orthodox_1920.png -resize 50% orthodox_1920.jpg
convert total_1920.png -resize 50% total_1920.jpg
cd ..