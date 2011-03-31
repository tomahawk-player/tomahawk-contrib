# -*- coding: utf8 -*-
#
# A class to construct simple XSPF playlists.
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


class SimpleXSPFGenerator(object):
	
	def __init__(self, title, creator, *args, **kwargs):
		
		stamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
		
		self.xml = u'<?xml version="1.0" encoding="UTF-8"?>\n'
		self.xml += u'<playlist version="1" xmlns="http://xspf.org/ns/0/">\n'
		self.xml += u' <creator>%s</creator>\n' % creator
		self.xml += u' <date>%s</date>\n' % stamp
		self.xml += u' <title>%s</title>\n' % title
		self.xml += u' <trackList>\n'
		
	
	def addTrack(self, **kwargs):
		"""
		Adds a track to the list. 
		Arguments must be key/value pairs corresponding	to XSPF child elements 
		under <track>.
		"""
		
		self.xml += u'  <track>\n'
		
		for k, v in kwargs.items():
			if k == "artist":
				k = "creator"
			self.xml += u'   <{k}>{v}</{k}>\n'.format(k=k, v=v)
			
		self.xml += u'  </track>\n'
	
	
	def addTracks(self, tracks):
		"""
		Adds multiple tracks to the list.
		'tracks' is a list of dicts, see addTrack().
		"""
		for track in tracks:
			self.addTrack(**track)
	
	
	def __unicode__(self):
		xml = self.xml + u' </tracklist>\n</playlist>'
		return xml
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	
