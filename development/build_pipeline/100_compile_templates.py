#!/usr/bin/env python

import os
import shutil
from jinja2 import Environment, FileSystemLoader
from util import fileutils as futil

def build(src_dir, dst_dir, opts):
  loader = FileSystemLoader(src_dir)
  env = Environment(auto_reload=False, trim_blocks=True, lstrip_blocks=True, loader=loader)

  # Render all files in the src_dir that have a ".j2" extension
  for (src_path, dst_path) in futil.pairwalk(src_dir, dst_dir):
    futil.try_mkdirs(os.path.dirname(dst_path))

    if futil.ext(src_path) == '.j2':
      template = os.path.basename(src_path)

      # If it starts with "_" then it is a partial
      if not template.startswith('_'):
        out_path = futil.chompext(dst_path)
        env.get_template(template).stream().dump(out_path)
    else:
      # Copy all other files straight over
      shutil.copy2(src_path, dst_path)

