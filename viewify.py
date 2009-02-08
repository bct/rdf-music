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
    _artists = []
    for uri in TripleStore.model.get_sources(ns['rdf'].type, ns['mo'].MusicArtist):
      name = str(TripleStore.model.get_target(uri, ns['foaf'].name))
      _artists.append((name, uri,))

    _artists.sort()

    return _artists

  def albums(self, artist_uri):
    # cache this, there's probably a better way...
    if not hasattr(self, '_artist_albums'):
      self._artist_albums = {}

      _albums = TripleStore.model.get_sources(ns['rdf'].type, ns['mo'].Record)
      for album_uri in _albums:
        a_uri = TripleStore.model.get_target(album_uri, ns['foaf'].maker)

        if not a_uri in self._artist_albums:
          self._artist_albums[a_uri] = []

        title = str(TripleStore.model.get_target(album_uri, ns['dc'].title))

        self._artist_albums[a_uri].append((title, album_uri,))

      for a_uri in self._artist_albums:
        self._artist_albums[a_uri].sort()

    if artist_uri in self._artist_albums:
      return self._artist_albums[artist_uri]
    else:
      return []

  def GET(self):
    web.header('Content-Type', 'text/html; charset=utf-8')

    out = '<ul>'

    for name, artist_uri in self.artists():
      out += '\n<li>' + name
      out += '\n<ul>'

      for title, album_uri in self.albums(artist_uri):
        out += '\n<li>' + title

      out += '\n</ul>'

    return out

app = web.application(urls, globals())

if __name__ == '__main__':
  app.run()
