#!/usr/bin/env python

import web

urls = (
  '/', 'index',
)

import RDF
import TripleStore

from Vocab import ns

class index:
  def artist_name(self, uri):
    return str(TripleStore.model.get_target(uri, ns['foaf'].name))

  def artists(self):
    _artists = []
    for uri in TripleStore.model.get_sources(ns['rdf'].type, ns['mo'].MusicArtist):
      name = self.artist_name(uri)
      _artists.append((name, uri,))

    # hardcoding this is yuk
    va_uri = 'http://zitgist.com/music/artist/89ad4ac3-39f7-470e-963a-56509c546377'
    va_uri = RDF.Node(RDF.Uri(va_uri))
    _artists.append(('Various Artists', va_uri,))

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
      _albums = self.albums(artist_uri)

      if len(_albums) == 0:
        continue

      out += '\n<li>' + name
      out += '\n  <ul>'

      for title, album_uri in _albums:
        out += '\n  <li>' + title

      out += '\n  </ul>'

    return out

app = web.application(urls, globals())

if __name__ == '__main__':
  app.run()
