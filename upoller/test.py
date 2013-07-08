import sys
import os
import logging
import yaml
import datetime

from lib import utils
from lib import pidmanager

from pprint import pprint

import requests

if __name__ == '__main__':
  timeout = 5
  #proxy = { 'http' : 'http://proxy.corp.globant.com:3128'}
  proxy={}

  r = requests.get('http://www.canalla.com', timeout=timeout, proxies=proxy)

  pprint(dir(r))

  print r.elapsed
  print r.connection
  print r.status_code
  print r.url
  print r.json
  print r.headers
  #print r.text


