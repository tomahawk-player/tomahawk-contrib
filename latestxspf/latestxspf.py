#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# This script creates an XSPF playlist containing the 
# latest additions to your local music collection.
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <mo@liberejo.de> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return - Remo Giermann.
# ----------------------------------------------------------------------------
#
# author:  Remo Giermann <mo@liberejo.de>
# created: 2011/03/30
#

import time
import urllib
import commands
import tagpy
import xspfgenerator
from find import *

class TagReader(object):
	"""
	Reads tags from filenames and saves it to a list of dictionaries.
	"""
	def __init__(self):
		self.__dicts = []
	
	def read(self, filename):
		"""
		Reads tag info from 'filename' and saves a dictionary with artist, title 
		and album strings.
		"""
		tag = tagpy.FileRef(filename).tag()
		d = {}
		d.update(location = 'file://'+urllib.quote(filename))
		d.update(artist = tag.artist or "Unknown Artist")
		d.update(title = tag.title or "Unknown Title")
		d.update(album = tag.album or '')
		
		self.__dicts.append(d)
	
	def tags(self):
		"""
		Returns all tags read so far in a list of dicts
		"""
		return self.__dicts
		

def latesttracks(directory, days):
	"""
	Finds the latest additions to 'directory' (within the last 'days')
	and returns an XSPF playlist.
	"""
	tags = TagReader()
	then = time.time() - (days * 24 * 3600)
	date = time.strftime("%D", time.localtime(then))
	now  = time.strftime("%D")
	
	creator = "LatestXSPF"
	title = "New tracks from {date} till {now}".format(date=date, now=now)
	
	find(days=days, dir=directory, exts=[".mp3", ".flac", ".ogg"], hook=tags.read)
	
	xspf = xspfgenerator.SimpleXSPFGenerator(title, creator)
	xspf.addTracks(tags.tags())
	return xspf


if __name__ == "__main__":
	import sys
	argv, argc = sys.argv, len(sys.argv)
	if argc < 3:
		print "Usage: %s DIRECTORY DAYS" % argv[0]
	elif not argv[2].isdigit():
		print "DAYS should be a number"
		sys.exit(1)
	else:
		print latesttracks(argv[1], int(argv[2]))
