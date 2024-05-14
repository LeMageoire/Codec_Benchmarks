#!/bin/sh

# Import all modules in the given directory
echo "Importing modules..."
git submodule init
git submodule update
echo "Done. libraries/ directory is now populated with all the modules."
