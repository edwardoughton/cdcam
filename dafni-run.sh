#!/usr/bin/env bash
set -e
set -x

# Extract data
unzip /data/inputs/zenodo-data-package.zip -d /data

# Run from output directory
cd /data/outputs

# Run model
python /code/run.py
