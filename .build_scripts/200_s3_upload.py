#!/usr/bin/env python

import boto3
import botocore
import os
import hashlib
import mimetypes
import itertools

def filehash(file):
  BLOCKSIZE = 65536
  hasher = hashlib.md5()

  with open(file, 'rb') as afile:
    buf = afile.read(BLOCKSIZE)
    while len(buf) > 0:
      hasher.update(buf)
      buf = afile.read(BLOCKSIZE)

  return hasher.hexdigest()

def build(base_dir, website_dir, build_dir):
  bucket_name = os.environ['S3_BUCKET']

  s3 = boto3.resource('s3')
  bucket = s3.Bucket(bucket_name)

  for (root, dirs, files) in os.walk(build_dir):
    for filename in files:
      path = os.path.join(root, filename)
      local_hash = filehash(path)

      key = os.path.relpath(path, build_dir)
      obj = bucket.Object(key)
      exists = False

      try:
        obj.load()
      except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] != "404":
          raise e
      else:
        exists = True

      if not exists or obj.metadata.get('hash') != local_hash:
        print "{} differs, uploading".format(path)
        (mime, _) = mimetypes.guess_type(path)
        obj.upload_file(path, ExtraArgs={'ContentType': mime, 'Metadata': {'hash': local_hash}})

