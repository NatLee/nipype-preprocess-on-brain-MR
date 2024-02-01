#!/bin/bash

# Clean files starting with "crash" in ./src directory
find ./src -name "crash-*.pklz" -exec rm -rf {} \;
