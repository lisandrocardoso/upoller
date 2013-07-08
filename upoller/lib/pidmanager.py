import sys
import os
import datetime
import logging

class PidMgr(object):
  def __init__(self, pidfile, pid):
    self.pidfile = pidfile
    self.pid = pid

    self.notify_thr = 24

    pid_from_file = self.check_pidfile(pidfile)

    if pid_from_file:
      logging.error("PidMgr: Pidfile already exists, check process runing with pid " + str(pid_from_file))
      if self.check_pidfile_ctime(pidfile):
        logging.critical("Existing pidfile " + str(pidfile) + " older than " + str(self.notify_thr) + " hours. Notifying.")
        self.notify_pidfile()
      sys.exit(1)
    else:
      self.set_pidfile(pidfile, pid)
      logging.info('PidMgr: running with PID ' + str(pid))

  def check_pidfile(self, pidfile):
    if os.path.exists(pidfile):
      with open(pidfile, 'r') as pidf:
        return pidf.readline()
    else:
      return False

  def set_pidfile(self, pidfile, pid):
    with open(pidfile, 'w') as pidf:
      pidf.write(str(pid))
      self.pidfile = pidfile
      self.pid = pid

  def clear_pidfile(self):
    os.unlink(self.pidfile)

  def check_pidfile_ctime(self, pidfile):
    """
      Check if pidfile is older than hours parameter
    """
    a = os.stat(pidfile)

    pidfiletime = datetime.datetime.fromtimestamp(a.st_ctime)
    now = datetime.datetime.today()
    difftime = datetime.timedelta(hours=self.notify_thr)

    if pidfiletime + difftime < now:
      return True

    return False

  def notify_pidfile(self):
    pass
