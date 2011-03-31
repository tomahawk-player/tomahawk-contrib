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

import commands, tagpy, xspfgenerator, urllib, time

findstring = 'find %s -mtime -%i -and \( -iname "*.mp3" -or -iname "*.ogg" -or -iname "*.flac" \)'


def findfiles(directory, mtime):
	"""
	Finds audio files in 'directory' modified in the last 'mtime' days.
	"""
	listing = commands.getoutput(findstring % (directory, mtime))
	return listing.split('\n')


def tag2dict(filename):
	"""
	Reads tag info from 'filename' and returns a dictionary with artist, title 
	and album strings.
	"""
	tag = tagpy.FileRef(filename).tag()
	d = {}
	d.update(location = 'file://'+urllib.quote(filename))
	d.update(artist = tag.artist or "Unknown Artist")
	d.update(title = tag.title or "Unknown Title")
	d.update(album = tag.album or '')
	
	return d


def latesttracks(directory, days):
	"""
	Finds the latest additions to 'directory' (within the last 'days')
	and returns an XSPF playlist.
	"""
	then = time.time() - (days * 24 * 3600)
	date = time.strftime("%m/%d, %Y", time.localtime(then))
	creator = "LatestXSPF"
	title = "New tracks since " + date
	files  = findfiles(directory, days)
	tracks = [tag2dict(f) for f in files]
	
	xspf = xspfgenerator.SimpleXSPFGenerator(title, creator)
	xspf.addTracks(tracks)
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
