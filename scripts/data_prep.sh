#!/bin/bash
set -e

cd ./data
echo "   Downloading data from https://doi.org/10.5281/zenodo.14286306"
echo "    ⚠️ Warning: this will use ~8GB"
wget -U firefox -c -O grid.tar https://zenodo.org/records/14286306/files/grid.tar
echo "   Unpacking data"
tar xvf grid.tar
echo "    ⚠️ Warning: this will use ~15GB"
for f in *.*rot*.tar.xz; do
    echo "     Create subfolder and unpack $f"
    mkdir -p "${f%.tar.xz}"
    tar -xzf "$f" -C "${f%.tar.xz}"
done
# tar xzvf grid.tar
echo "   Downloading data from https://doi.org/10.5281/zenodo.11375523"
echo "   for 22-isotope network model"
mkdir -p ./SMALL_NET/
cd ./SMALL_NET
wget -U firefox https://zenodo.org/records/11375523/files/40_rot0.6_small_net.tar.xz
echo "   Upacking "
tar xzvf 40_rot0.6_small_net.tar.xz
cd ..
cd ../
