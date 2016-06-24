#!/usr/bin/env python

import os
import shutil
import subprocess
import datetime
import dateutil.parser
from dateutil.tz import tzstr
from subprocess import Popen, PIPE
from jinja2 import Environment, FileSystemLoader
from util import fileutils as futil

def commitDate(path):
  git = Popen(['git', 'log', '--format=%ai', '--reverse', path], stdout=PIPE)

  post_date = datetime.datetime.now().isoformat()
  for line in git.stdout:
    post_date = line.strip()
    break;

  git.terminate()
  git.wait()

  return post_date


def build(src_dir, dst_dir, opts):
  loader = FileSystemLoader(src_dir)
  env = Environment(auto_reload=False, trim_blocks=True, lstrip_blocks=True, loader=loader)
  env.globals['environment'] = opts.get('environment')

  posts = []

  for (root, dirs, files) in os.walk(os.path.join(src_dir, 'posts')):
    for f in files:
      if f.startswith('_'):
        template_path = os.path.join(root, f)

        post_date = commitDate(template_path)

        date = dateutil.parser.parse(post_date).astimezone(tzstr("PST8PDT"))
        pretty_date = date.strftime('%A, %B ') + str(date.day) +\
            date.strftime(', %Y')

        template_path = os.path.relpath(template_path, src_dir)
        posts.append((post_date, pretty_date, template_path))

  env.globals['post_templates'] = sorted(posts, reverse=True)

  # Render all files in the src_dir that have a ".j2" extension
  for (src_path, dst_path) in futil.pairwalk(src_dir, dst_dir):
    futil.try_mkdirs(os.path.dirname(dst_path))

    if futil.ext(src_path) == '.j2':
      template = os.path.relpath(src_path, src_dir)

      # If it starts with "_" then it is a partial
      if not os.path.basename(template).startswith('_'):
        out_path = futil.chompext(dst_path)
        env.get_template(template).stream().dump(out_path)
    elif not src_path.endswith(('.swp', '~')):
      # Copy all other files straight over
      shutil.copy2(src_path, dst_path)

