# -*- coding: utf8 -*-
#
# Finding files with python
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <mo@liberejo.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Remo Giermann.
# ----------------------------------------------------------------------------
#
# author:  Remo Giermann
# created: 2011/04
#

import os
import sys
import time

def check_extension(filename, exts):
	"""
	Checks if 'filename' has any of 'exts' as its
	extension and returns it if so.
	"""
	for ext in exts:
		if filename.lower().endswith(ext.lower()):
			return ext
	return ''

def check_mtime(path, days):
	"""
	Checks creation and modification time of 'path' and returns
	True if it was modified or created in the last 'days' days
	False otherwise.
	"""
	stats = os.stat(path)
	mtime = stats.st_mtime
	ctime = stats.st_ctime
	
	now = time.time()
	then = now - days*24*3600	
	return mtime > then or ctime > then

def find(dir, name='', exts=[], days=0, hook=None):
	"""
	Find and print files in 'dir'.
	If 'name' is set, print only files with that string
	in their names.
	If 'exts' is set to a list of file extensions, only
	print files having these extensions. 	
	If 'days' is not 0, print only files modified in the 
	last 'days' days.
	If 'hook' is callable, then it will be on any
	file found (matching above criteria) with the filename 
	as an argument or if 'hook' has an append method, 
	each found name will be appended to it, in both cases
	nothing will be printed.	
	"""
	if hasattr(hook, '__call__'):
		call = hook
	elif hasattr(hook, 'append'):
		call = hook.append
	else:
		call = None
		

	for dirpath, dirs, files in os.walk(dir):
		rm = []
		for d in dirs:
			path = os.path.join(dirpath, d)
			if days > 0 and check_mtime(path, days) is False:
				dirs.remove(d)

		for i in rm:
			del dirs[i]

		for f in files:
			path = os.path.join(dirpath, f)
			if len(exts) == 0 or check_extension(f, exts) in exts:
				if days == 0 or check_mtime(path, days) is True:
					if call is None:
						print path
					else:
						call(path)


#------------------------------------------------------------------------------
if __name__ == '__main__': 
	from sys import argv, exit
	from timeit import Timer
	import commands

	def gnufind(directory, mtime):
		findstring = 'find %s -mtime -%i -and \( -iname "*.mp3" -or -iname "*.ogg" -or -iname "*.flac" \)'
		commands.getoutput(findstring % (directory, mtime))
	
	usage = """
to compare gnufind and pytfind run
{0} COUNT DIRECTORY DAYS

Starting both functions to look for  music files modified
within the last DAYS in DIRECTORY.
This is run COUNT times and the timing results are printed.
""".format(argv[0])

	if len(argv) < 4:
		print usage
		exit(1)

	exts = ['.mp3', '.ogg', '.flac']
	count = int(argv[1])
	path = argv[2]
	days = int(argv[3])
	print "looking in {path} for music from the last {days} days - repeating {c} times...".format(path=path, days=days, c=count)

	gnu = Timer("gnufind(path, days)", "from __main__ import gnufind, path, days")
	pyt = Timer("find(exts=exts, dir=path, days=days, hook=[])", "from __main__ import find, path, days, exts")
	tpyt = pyt.repeat(number=1, repeat=count)
	tgnu = gnu.repeat(number=1, repeat=count)
	
	print "gnufind: {min:0<6.4}, {avg:0<6.4}, {max:0<6.4}".format(min=min(tgnu), max=max(tgnu), avg=sum(tgnu)/count)
	print "pytfind: {min:0<6.4}, {avg:0<6.4}, {max:0<6.4}".format(min=min(tpyt), max=max(tpyt), avg=sum(tpyt)/count)
