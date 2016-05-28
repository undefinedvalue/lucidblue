#!/usr/bin/env python

import SimpleHTTPServer
import SocketServer
import os
import threading
import signal
import watchdog
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
import build_pipeline.build

class Server:
  def __init__(self, src_dir, dst_dir, port=8080, **kwargs):
    self.src_dir = src_dir
    self.dst_dir = dst_dir
    self.port = port
    self.final_build_dir = os.path.join(self.dst_dir, 'final')
    self.build_sem = threading.Semaphore()
    self.httpd = None
    self.server_thread = None

  def start(self):
    filewatch = Observer()
    filewatch.schedule(FilewatchHandler(parent=self, ignore_patterns=['*.swp', '*~']), self.src_dir, recursive=True)

    # Clean shutdown on ctrl+c
    def signal_handler(signal, frame):
      print
      print 'Shutting down...'
      self.stop_server()
      filewatch.stop()

    signal.signal(signal.SIGINT, signal_handler)

    self.rebuild()
    self.start_server()

    print 'Serving at port', self.port
    print 'Serving files from', self.final_build_dir
    print('Press Ctrl+C to stop')

    filewatch.start()
    signal.pause()
    filewatch.join(5000)

  def rebuild(self):
    self.build_sem.acquire()
    try:
      print 'Building', self.src_dir
      build_pipeline.build.build(self.src_dir, self.dst_dir, skip=['s3_upload'])
      os.chdir(self.final_build_dir)
    finally:
      self.build_sem.release()

  def server(self):
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    self.httpd = SocketServer.TCPServer(('', self.port), Handler)

    self.httpd.serve_forever()
    self.httpd.server_close()
    print 'Server stopped'

  def start_server(self):
    print 'Starting server'
    self.server_thread = threading.Thread(target=lambda: self.server())
    self.server_thread.start()

  def stop_server(self):
    if self.httpd:
      print 'Stopping server'
      self.httpd.shutdown()
      self.server_thread.join(5000)

class FilewatchHandler(PatternMatchingEventHandler):
  def __init__(self, parent, *args, **kwargs):
    super(FilewatchHandler, self).__init__(*args, **kwargs)
    self.parent = parent

  def on_created(self, event):
    if not event.is_directory:
      print 'Detected change in', event.src_path
      self.parent.rebuild()

