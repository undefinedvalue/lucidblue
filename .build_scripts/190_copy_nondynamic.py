#!/usr/bin/env python

import os
from os.path import relpath, join
import shutil

def build(base_dir, website_dir, build_dir):
  # Copy files from the website_dir to the build_dir that do not already exist
  # there and do not start with "_" (which indicates a partial)
  for (root, dirs, files) in os.walk(website_dir):
    to_copy = [f for f in files if not f.startswith('_')]
    # Just get the part of the path after the website_dir
    to_copy = [relpath(join(root, f), website_dir) for f in to_copy]
    # Only copy nonexistant
    to_copy = [f for f in to_copy if not os.path.exists(join(build_dir, f))]

    for filename in to_copy:
      src_path = join(website_dir, filename)
      dst_path = join(build_dir, filename)
      dst_dir = os.path.dirname(dst_path)

      if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)

      shutil.copy(src_path, dst_path)
