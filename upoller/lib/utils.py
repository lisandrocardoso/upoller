import argparse
import logging
import sys

def parse_cmd_line():
  options = argparse.ArgumentParser(description="Proxy Police proxy status poller.")
  options.add_argument("-s", "--single_run", help="Don't fork, run just this once, output to STDOUT.",
    action="store_true")
  options.add_argument("-c", "--config_file", default="./config.yaml",
    help="Config file", metavar="FILE", type=argparse.FileType('r'), required=True)
  options.add_argument("-d", "--debug", help="Run in debug mode, log more stuff.", action="store_true")
  #options.add_argument("-i", "--poll-interval", help ="Polling interval, to use with -d.")
  return options.parse_args()

def setup_logging(level, stream = True, filename = None):
  logformat = "%(asctime)s %(name)s %(levelname)s %(message)s"
  formatter = logging.Formatter(logformat)

  for h in logging.getLogger('PP').handlers:
    logging.getLogger('PP').removeHandler(h)

  if stream:
    logging.getLogger('PP').setLevel(level)
    logging.getLogger('PP').propagate = False

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    logging.getLogger('PP').addHandler(stdout_handler)

  if filename:
    logging.getLogger('PP').removeHandler(logging.FileHandler(filename))
    logging.getLogger('PP').setLevel(level)
    logging.getLogger('PP').propagate = False

    handler = logging.FileHandler(filename)
    handler.setFormatter(formatter)
    logging.getLogger('PP').addHandler(handler)
