#!/usr/bin/env python

import web

urls = (
  '/', 'index',
)

import RDF
import TripleStore

from Vocab import ns

class index:
  def artists(self):
    return TripleStore.model.get_sources(ns['rdf'].type, ns['mo'].MusicArtist)

  def albums(self, artist_uri):
    # cache this, there's probably a better way...
    if not hasattr(self, '_album_artists'):
      self._album_artists = {}

      _albums = TripleStore.model.get_sources(ns['rdf'].type, ns['mo'].Record)
      for album_uri in _albums:
        a_uri = TripleStore.model.get_target(album_uri, ns['foaf'].maker)

        if not a_uri in self._album_artists:
          self._album_artists[a_uri] = []

        self._album_artists[a_uri].append(album_uri)

    if artist_uri in self._album_artists:
      return self._album_artists[artist_uri]
    else:
      return []

  def GET(self):
    web.header('Content-Type', 'text/html; charset=utf-8')

    out = '<ul>'

    for artist_uri in self.artists():
      name = TripleStore.model.get_target(artist_uri, ns['foaf'].name)
      out += '\n<li>' + str(name)
      out += '\n<ul>'

      for album_uri in self.albums(artist_uri):
        title = TripleStore.model.get_target(album_uri, ns['dc'].title)
        out += '\n<li>' + str(title)

      out += '\n</ul>'

    return out

app = web.application(urls, globals())

if __name__ == '__main__':
  app.run()
