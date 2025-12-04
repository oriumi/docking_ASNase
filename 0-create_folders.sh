#!/bin/bash

for f in *.pdb; do
    dirname="${f%.pdb}"
    mkdir -p "$dirname"
    mv "$f" "$dirname/"
done
