import sys
import os
import logging
import yaml
import datetime

from lib import utils
from lib import poller
from lib import pidmanager

from pprint import pprint

if __name__ == '__main__':
  options = utils.parse_cmd_line()
  config = yaml.load(options.config_file)

  logformat = "%(asctime)s %(levelname)s %(message)s"
  log_file_name = config.get('log_file').format(datetime.datetime.now())


  if options.debug:
    loglevel = logging.DEBUG
  else:
    loglevel = logging.INFO

  logging.basicConfig(format = logformat, level = loglevel)

  if not options.single_run:
    pid = os.fork()
    if pid:
      sys.exit(0)
    logging.info("Running in background")
    utils.setup_logging(loglevel, stream = False, filename = log_file_name)
    pid = os.getpid()
  else:
    pid = os.getpid()
    logging.info("Single run mode")
    utils.setup_logging(loglevel, stream = True, filename = log_file_name)

  pm = pidmanager.PidMgr(config.get('pid_file'), pid)

  logging.getLogger('PP').info("ProxyPolice 0.1")

  p = poller.Poller(config, (not options.single_run))
  p.start_poller()

  pm.clear_pidfile()

