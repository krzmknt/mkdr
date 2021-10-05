i#!/bin/bash

printf '\e[34mmkdir release\e[m\n';
mkdir release;
printf '\e[34mcp README.md -> release\e[m\n';
cp README.md release;
printf '\e[34mpyinstaller gch\e[m\n';
pyinstaller mkdr.py --onefile && mv dist/mkdr release/
printf '\e[34mtar zcvf\e[m\n';
tar zcvf mkdr.tar.gz release
printf '\e[34mrm -rf build, dist, release\e[m\n';
rm -rf build
rm -rf dist
rm -rf release
printf '\e[34mrm spec filest\e[m\n';
rm *.spec
