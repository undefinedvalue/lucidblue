#!/usr/bin/env python

import os
import shutil
import importlib
import re

NAME_RE = re.compile(r'\A(\d\d\d_(\w+))\.py\Z')

def build(src_dir, dst_dir, skip=[], opts={}, **kwargs):
  build_script_dir = os.path.dirname(os.path.abspath(__file__))
  build_module_name = os.path.basename(build_script_dir)

  if os.path.isdir(dst_dir):
    # Clean out files except module build dirs
    for mod_dir in os.listdir(dst_dir):
      for path in os.listdir(os.path.join(dst_dir, mod_dir)):
        fullpath = os.path.join(dst_dir, mod_dir, path)
        if os.path.isdir(fullpath):
          shutil.rmtree(os.path.join(dst_dir, mod_dir, path))
        else:
          os.remove(fullpath)
  else:
    os.mkdir(dst_dir)

  # Import each file, sorted by name, except for the current script
  curr_src_dir = src_dir
  for path in sorted(os.listdir(build_script_dir)):
    filename = os.path.basename(path)
    m = NAME_RE.match(filename)

    if m is None:
      continue

    (mod_name, name) = m.group(1, 2)

    if name not in skip:
      print "Executing {}".format(mod_name)
      mod = importlib.import_module(build_module_name + '.' + mod_name)
      curr_dst_dir = os.path.join(dst_dir, mod_name)

      mod.build(curr_src_dir, curr_dst_dir, opts)

      curr_src_dir = curr_dst_dir

  final_dir = os.path.join(dst_dir, 'final')

  if os.path.exists(final_dir):
    os.remove(final_dir)

  os.symlink(curr_src_dir, final_dir)

