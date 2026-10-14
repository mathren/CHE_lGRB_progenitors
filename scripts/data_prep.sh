#!/bin/bash
set -e

cd ./data
echo "   Downloading data from https://doi.org/10.5281/zenodo.14286306"
echo "    ⚠️ Warning: this will use ~8GB"
wget -c -O mesa_128.net "https://zenodo.org/records/23348863/files/mesa_128.net?download=1"
wget -c -O approx21_cr60_plus_co56.net "https://zenodo.org/records/23348863/files/approx21_cr60_plus_co56.net?download=1"
wget -c -O store_net_info.txt "https://zenodo.org/records/23348863/files/store_net_info.txt?download=1"
wget -c -O grid.tar "https://zenodo.org/records/23348863/files/grid.tar?download=1"
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
