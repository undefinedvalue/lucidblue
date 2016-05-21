#!/usr/bin/env python

import boto3
import botocore
import os
import hashlib
import mimetypes
from util import fileutils as futil

def filehash(file):
  BLOCKSIZE = 65536
  hasher = hashlib.md5()

  with open(file, 'rb') as afile:
    buf = afile.read(BLOCKSIZE)
    while len(buf) > 0:
      hasher.update(buf)
      buf = afile.read(BLOCKSIZE)

  return hasher.hexdigest()

def build(base_dir, source_dir, build_dir):
  bucket_name = os.environ['S3_BUCKET']

  s3 = boto3.resource('s3')
  bucket = s3.Bucket(bucket_name)

  for (src_path, s3_key) in futil.pairwalk(source_dir, ''):
    local_hash = filehash(src_path)

    obj = bucket.Object(s3_key)
    exists = False

    try:
      obj.load()
    except botocore.exceptions.ClientError as e:
      if e.response['Error']['Code'] != "404":
        raise e
    else:
      exists = True

    if not exists or obj.metadata.get('hash') != local_hash:
      print "{} differs, uploading".format(src_path)
      (mime, _) = mimetypes.guess_type(src_path)
      obj.upload_file(src_path, ExtraArgs={'ContentType': mime, 'Metadata': {'hash': local_hash}})

