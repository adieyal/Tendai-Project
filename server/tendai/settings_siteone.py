try:
	from settings import *
except ImportError:
	import sys
	sys.stderr.write("Unable to read settings.py\n")
	sys.exit(1)

#SPATIALITE_LIBRARY_PATH = "/home/sarpam/lib/libspatialite.so"
SITE_ID = 1
