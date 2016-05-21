#!/usr/bin/env python

import sass
import os
import shutil
from util import fileutils as futil

def build(base_dir, source_dir, build_dir):
  sass.compile(dirname=(source_dir, build_dir))

  # Copy non-scss files over
  for (src_path, dst_path) in futil.pairwalk(source_dir, build_dir):
    if futil.ext(src_path) != '.scss':
      futil.try_mkdirs(os.path.dirname(dst_path))
      shutil.copy2(src_path, dst_path)
