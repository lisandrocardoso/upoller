import sys
import os
import threading
import time
import Queue
import logging
import requests

from pprint import pprint

class Poller():
  def __init__(self, config, daemon = True):
    self.config = config
    self.poll_config = {
      'proxy' : 'http://' + config.get('poller_proxy_url') + ':' + str(config.get('poller_proxy_port')),
      'interval' : config.get('poller_interval'),
      'timeout' : config.get('poller_timeout')
    }
    self.daemon = daemon
    self.q = Queue.Queue()
    self.url_track = {}


    self.logger = logging.getLogger('PP')
    self.logger.info("Polled URLs:")
    for url in self.config.get('poller_urls', []):
      self.logger.info("   " + url)
      # (url, bool) : <url>, <last run state where True = OK>
      self.q.put((url, True))
      self.url_track[url] = 0
    self.logger.info("Polling interval: " + str(self.config.get('poller_interval', 0)))
    self.logger.info("Proxy settings : " + self.config.get('poller_proxy_url') + ", " +
                     str(self.config.get('poller_proxy_port')))

  def start_poller(self):
    if self.daemon:
      self.logger.info("Running in daemon mode.")
      while True:
        (url, last) = self.q.get(block = True)
        if not last:
          self.url_track[url] += 1
        else:
          self.url_track[url] = 0

        if self.url_track[url] > self.config.get('poller_threshold'):
          logging.getLogger('PP').error('URL ' + url + ' failed ' + str(self.url_track.get(url)) + ' time/s')

        p_config = self.poll_config.copy()
        p_config['url'] = url
        t = threading.Thread(target = self.do_poll, args = (self.q, p_config))
        t.daemon = True
        t.start()
    else:
      self.logger.info("Running in single-run mode.")
      for url in self.config.get('poller_urls', []):
        p_config = self.poll_config.copy()
        p_config['url'] = url
        p_config['interval'] = 0

        #pprint(p_config)
        t = threading.Thread(target = self.do_poll, args = (self.q, p_config))
        t.daemon = True
        t.start()

      while threading.active_count() != 1:
        # We wait for our threads to finish
        pass


  def do_poll(self, q, p_config):
    #print "Thread Start " + url + " " + str(interval)
    tname = threading.current_thread().name
    logging.getLogger('PP').debug('Thread ' + tname + ' started, polling ' + p_config.get('url'))
    start_time = time.time()

    try:
      r = requests.get(p_config.get('url'), proxies={ 'proxy': p_config.get('proxy') }, timeout=p_config.get('timeout'))
    except:
      r = None

    if r:
      logging.getLogger('PP').debug(tname + ' Return code: ' + str(r.status_code))
      time.sleep(p_config.get('interval'))
      if r.status_code == 200:
        q.put((p_config.get('url'), True))
      else:
        q.put((p_config.get('url'), False))
    else:
      logging.getLogger('PP').warn(tname + ' failed: ' + p_config.get('url'))
      time.sleep(p_config.get('interval'))
      q.put((p_config.get('url'), False))

    end_time = time.time()
    diff_time = end_time - start_time
    logging.getLogger('PP').debug('Thread ' + tname + ' execution time: ' + str(diff_time))
    #print "Thread Done " + url

