#!/usr/bin/env bash

echo "Compiling main interface..."
path="/home/celis/power_supply_sim"

pyinstaller "main.spec"
echo "Copying executable...11/5"
cp -R "dist/main" "$path/main"
echo "removing temporaly files...12/5"
rm -rf "./dist"
rm -rf "./build"
rm -rf "./__pycache__"

echo "Compiled drivers..."


