import time
from sys import argv

def log_time():
	tm = time.localtime(time.time())
	timestr = "%s/%s/%s %02s:%02s:%02s" % (tm[1], tm[2], tm[0], tm[3], tm[4], tm[5])
	return timestr

def log(logfile, func, msg):
	if(logfile is not None):
		fout = open(logfile, "a")
		fout.write("%s %s.%s: %s" % (log_time(), argv[0], func, msg))
		fout.close()

def log_and_print(logfile, func, msg):
	log(logfile, func, msg)
	print "%s %s.%s: %s" % (log_time(), argv[0], func, msg)
