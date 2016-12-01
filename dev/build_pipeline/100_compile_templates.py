#!/usr/bin/env python

# Compiles Jinja templates (.j2 extension)

import os
import shutil
import subprocess
import datetime
import dateutil.parser
from dateutil.tz import tzstr, tzlocal
from subprocess import Popen, PIPE
from jinja2 import Environment, FileSystemLoader
from util import fileutils as futil

# Returns the date of the first commit in git of the given file.
# If the file is not committed in git, just returns the current date.
def commitDate(path):
  git = Popen(['git', 'log', '--format=%ai', '--reverse', path], stdout=PIPE)

  commit_date = datetime.datetime.now(tzlocal()).isoformat()
  for line in git.stdout:
    commit_date = line.strip()
    break;

  git.terminate()
  git.wait()

  return commit_date


def build(src_dir, dst_dir, opts):
  loader = FileSystemLoader(src_dir)
  env = Environment(auto_reload=False,
                    trim_blocks=True,
                    lstrip_blocks=True,
                    loader=loader)
  env.globals['environment'] = opts.get('environment')

  posts = []

  # Make a list of the post templates and their commit dates
  for (root, dirs, files) in os.walk(os.path.join(src_dir, 'posts')):
    for f in files:
      if not f.startswith('.') and not f == 'index.html.j2':
        template_path = os.path.join(root, f)

        date = commitDate(template_path)
        date = dateutil.parser.parse(date).astimezone(tzstr("PST8PDT"))

        template_path = os.path.relpath(template_path, src_dir)
        posts.append((date, template_path))

  # Sort the posts by commit date so the newest post is first
  posts = sorted(posts, reverse=True)
  post_data = {}

  # Generate a hash of data needed for each post
  for idx, (date, template_path) in enumerate(posts):
    # A displayable version of the date
    pretty_date = date.strftime('%A, %B ') + \
        str(date.day) + date.strftime(', %Y')

    # Grab the post's title from it's "posttitle" block
    template = env.get_template(template_path)
    ctx = template.new_context()
    title = ' '.join(template.blocks['posttitle'](ctx)).strip()

    # Generate the relative URL of the post for use in links
    post_path = '/' + template.name
    if post_path.endswith('.j2'):
        post_path = post_path[:-3]

    post_data[template.name] = {
      'index': idx,
      'date': date,
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

