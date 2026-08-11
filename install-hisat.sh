#!/bin/bash
set -e

dest=${TARGET-/usr/}/bin
echo "using $dest as installation directory"
mkdir -p "$dest"

VERSION='2.2.1'
wget "https://cloud.biohpc.swmed.edu/index.php/s/oTtGWbWjaxsQ2Ho/download" -O hisat2-${VERSION}-Linux_x86_64.zip
unzip hisat2-${VERSION}-Linux_x86_64.zip
rm hisat2-${VERSION}-Linux_x86_64.zip

cd hisat2-${VERSION}
cp *.py "$dest"
cp hisat2* "$dest"
cd ..
rm -rf hisat2-${VERSION}

ver=$(hisat2 --version)
echo "${ver} is successfully installed"