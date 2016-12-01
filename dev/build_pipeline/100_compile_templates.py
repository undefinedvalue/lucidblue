#!/usr/bin/env python

import os
import shutil
import subprocess
import datetime
import dateutil.parser
from dateutil.tz import tzstr, tzlocal
from subprocess import Popen, PIPE
from jinja2 import Environment, FileSystemLoader
from util import fileutils as futil

def commitDate(path):
  git = Popen(['git', 'log', '--format=%ai', '--reverse', path], stdout=PIPE)

  post_date = datetime.datetime.now(tzlocal()).isoformat()
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
      if not f.startswith('.') and not f == 'index.html.j2':
        template_path = os.path.join(root, f)

        post_date = commitDate(template_path)
        post_date = dateutil.parser.parse(post_date).astimezone(tzstr("PST8PDT"))

        template_path = os.path.relpath(template_path, src_dir)
        posts.append((post_date, template_path))

  posts = sorted(posts, reverse=True)
  post_data = {}

  for idx, (post_date, template_path) in enumerate(posts):
    pretty_date = post_date.strftime('%A, %B ') + str(post_date.day) + post_date.strftime(', %Y')

    template = env.get_template(template_path)
    ctx = template.new_context()
    title = ' '.join(template.blocks['posttitle'](ctx)).strip()

    post_path = '/' + template.name
    if post_path.endswith('.j2'):
        post_path = post_path[:-3]

    post_data[template.name] = {
      'index': idx,
      'date': post_date,
      'pretty_date': pretty_date,
      'template': template_path,
      'title': title,
      'path': post_path
    }

  env.globals['post_templates'] = map(lambda x: x[1], posts)
  env.globals['post_data'] = post_data

  # Render all files in the src_dir that have a ".j2" extension
  for (src_path, dst_path) in futil.pairwalk(src_dir, dst_dir):
    futil.try_mkdirs(os.path.dirname(dst_path))

    if futil.ext(src_path) == '.j2':
      template = os.path.relpath(src_path, src_dir)

      # If it starts with "_" then it is a partial
      if not os.path.basename(template).startswith('_'):
        env.globals['template_name'] = template
        out_path = futil.chompext(dst_path)
        env.get_template(template).stream().dump(out_path)
    elif not src_path.endswith(('.swp', '~')):
      # Copy all other files straight over
      shutil.copy2(src_path, dst_path)

