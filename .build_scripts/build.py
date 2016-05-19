#!/usr/bin/env python

import os
import shutil
import importlib

# Get the name of this current script without the extension
(build_script_dir, curr_filename) = os.path.split(os.path.abspath(__file__))
(curr_filename, _) = os.path.splitext(curr_filename)

# Get the filenames without extension in the same directory as this script
files = [os.path.splitext(os.path.basename(f)) for f in os.listdir(build_script_dir)]
files = [n for (n, e) in files if e == '.py']

# Set up directories used by other scripts
base_dir = os.path.dirname(build_script_dir)
website_dir = os.path.join(base_dir, 'www')
build_dir = os.path.join(base_dir, 'build')

if os.path.isdir(build_dir):
  shutil.rmtree(build_dir)

os.mkdir(build_dir)

# Import each file, sorted by name, except for the current script
for f in sorted(files):
  if f != curr_filename:
    print "Executing {}".format(f)
    mod = importlib.import_module(f)
    mod.build(base_dir=base_dir, website_dir=website_dir, build_dir=build_dir)
