#!/usr/bin/env python

import os
from os.path import splitext, relpath, join
from jinja2 import Environment, FileSystemLoader

def build(base_dir, website_dir, build_dir):
  extensions = ['.html', '.css', '.js']
  loader = FileSystemLoader(website_dir)
  env = Environment(auto_reload=False, loader=loader)

  # Render all files in the website_dir that have the above extensions and do
  # not start with "_" (which indicates a partial)
  for (root, dirs, files) in os.walk(website_dir):
    templates = [f for f in files if splitext(f)[1] in extensions]
    templates = [t for t in templates if not t.startswith('_')]
    # Just get the part of the path after the website_dir
    templates = [relpath(join(root, t), website_dir) for t in templates]

    for template in templates:
      out_file = join(build_dir, template)
      out_dir = os.path.dirname(out_file)

      if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

      env.get_template(template).stream().dump(out_file)
