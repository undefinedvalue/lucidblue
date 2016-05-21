#!/usr/bin/env python

import os
import shutil
from jinja2 import Environment, FileSystemLoader
from util import fileutils as futil

def build(base_dir, source_dir, build_dir):
  loader = FileSystemLoader(source_dir)
  env = Environment(auto_reload=False, loader=loader)

  # Render all files in the source_dir that have a ".j2" extension
  for (src_path, dst_path) in futil.pairwalk(source_dir, build_dir):
    futil.try_mkdirs(os.path.dirname(dst_path))

    if futil.ext(src_path) == '.j2':
      # If it starts with "_" then it is a partial
      if not src_path.startswith('_'):
        template = os.path.basename(src_path)
        out_path = futil.chompext(dst_path)

        env.get_template(template).stream().dump(out_path)
    else:
      # Copy all other files straight over
      shutil.copy2(src_path, dst_path)

