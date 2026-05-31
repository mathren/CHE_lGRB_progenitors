#!/bin/bash
set -e

cd ./data
echo "   Downloading data from https://doi.org/10.5281/zenodo.14286306"
echo "     Warning: this will use ~8GB"
wget -qO- https://zenodo.org/api/records/14286306 | jq -r '.files[].links.self' | xargs -n1 wget -q --content-disposition
echo "   Unpacking data"
echo "     Warning: this will use ~15GB"
tar xzvf grid.tar
cd ../
