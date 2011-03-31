#!/usr/bin/env python
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

import commands, tagpy, xspfgenerator

findstring = 'find %s -mtime -%i -and \( -iname "*.mp3" -or -iname "*.ogg" -or -iname "*.flac" \)'


def findfiles(directory, mtime):
	listing = commands.getoutput(findstring % (directory, mtime))
	return listing.split('\n')


def tag2dict(filename):
	tag = tagpy.FileRef(filename).tag()
	d = {}
	d.update("artist", tag.artist or "Unknown Artist")
	d.update("title", tag.title or "Unknown Title")
	d.update("album", tag.album or '')
	
	return d


class Tracklist(object):
	"""
	Holds a list of music files, generates a list of tracks and may
	generate an XSPF playlist.
	"""

	def __init__(self, files):
		self.files  = files
		self.tracks = []
	
	def parseFiles(self):
		self.tracks = [tag2dict(f) for f in self.files]
	
	def genXSPF(self):
		xspf = xspfgenerator.SimpleXSPFGenerator()
		for t in self.tracks:
			xspf.addTrack(t)
		
		return str(xspf)



if __name__ == "__main__":
	import sys
	argv, argc = sys.argv, len(sys.argv)
	if argc < 3:
		print "Usage: %s DIRECTORY DAYS" % argv
	else:
		files = findfiles(argv[1], argv[2])
		t = Tracklist(files)
		t.parseFiles()
		print t.genXSPF()
