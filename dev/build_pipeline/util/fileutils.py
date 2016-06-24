#!/usr/bin/env python

import os
import itertools

def pairwalk(src_dir, dst_dir):
  for (root, dirs, files) in os.walk(src_dir):
    for f in files:
      src_path = os.path.join(root, f)
      dst_path = os.path.join(dst_dir, os.path.relpath(src_path, src_dir))

      yield (src_path, dst_path)

def filter_ext(allowed_exts, iterator):
  return itertools.ifilter(lambda f: ext(f) in allowed_ext, iterator)

def chompext(path):
  return os.path.splitext(path)[0]

def ext(path):
  return os.path.splitext(path)[1]

def try_mkdirs(path):
  if not os.path.isdir(path):
    os.makedirs(path)

