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

from xml.dom.minidom import Document
import time


class SimpleXSPFGenerator(Document):
	
	def __init__(self, title, creator, *args, **kwargs):
		Document.__init__(self, *args, **kwargs)
		
		stamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
		
		playlist = self.createElement("playlist")
		playlist.setAttribute("version", "1")
		playlist.setAttribute("xmlns", "http://xspf.org/ns/0/")
		self.appendChild(playlist)
		
		date = self.createElement("date")
		date.appendChild(self.createTextNode(stamp))
		playlist.appendChild(date)
		
		titletag = self.createElement("title")
		titletag.appendChild(self.createTextNode(title))
		playlist.appendChild(titletag)
		
		creatortag = self.createElement("creator")
		creatortag.appendChild(self.createTextNode(creator))
		playlist.appendChild(creatortag)
				
		tracklist = self.createElement("tracklist")
		playlist.appendChild(tracklist)
		
		self._playlist = playlist
		self._tracklist = tracklist
	
		
	def addTrack(self, **kwargs):
		"""
		Adds a track to the list. 
		Arguments must be key/value pairs corresponding	to XSPF child elements 
		under <track>.
		"""
		
		track = self.createElement("track")
		
		for k, v in kwargs.items():
			if k == "artist":
				k = "creator"
			child = self.createElement(k)
			child.appendChild(self.createTextNode(v))
			track.appendChild(child)
			
		self._tracklist.appendChild(track)
	
	
	def addTracks(self, tracks):
		"""
		Adds multiple tracks to the list.
		'tracks' is a list of dicts, see addTrack().
		"""
		for track in tracks:
			self.addTrack(**track)
	
	
	def __unicode__(self):
		return unicode(self.toprettyxml(indent='', encoding='utf-8'), 'utf-8')
	
	def __str__(self):
		return unicode(self).encode('utf-8')
	
	