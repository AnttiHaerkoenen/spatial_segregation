#!/usr/bin/env bash

cd slides
pandoc -s --mathml -i -t dzslides slides-2019-10-07.md -o slides-2019-10-07.html
sed -i 's/font-size: 80px/font-size: 55px/g' slides-2019-10-07.html
convert orthodox_1880.png orthodox_1880.jpg
convert total_1880.png total_1880.jpg
convert orthodox_1900.png orthodox_1900.jpg
convert total_1900.png total_1900.jpg
convert orthodox_1920.png orthodox_1920.jpg
convert total_1920.png total_1920.jpg
cd ..