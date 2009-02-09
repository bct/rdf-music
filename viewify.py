#!/usr/bin/env python

import web

urls = (
  '/', 'index',
)

render = web.template.render('templates/')

import RDF
import TripleStore

from Vocab import ns

class index:
  def artists_albums(self):
    # get a dict of all albums, keyed by artist URI
    albums = {}

    _albums = TripleStore.model.get_sources(ns['rdf'].type, ns['mo'].Record)
    for album_uri in _albums:
      artist_uri = TripleStore.model.get_target(album_uri, ns['foaf'].maker)
      title = str(TripleStore.model.get_target(album_uri, ns['dc'].title))

      if not artist_uri in albums:
        albums[artist_uri] = []

      albums[artist_uri].append((title, album_uri,))

    # get a list of all artists with an album in the dict
    artists = []

    for artist_uri in albums.keys():
      name = self.artist_name(artist_uri)
      artists.append((name, artist_uri,))

    return (artists, albums)

  def artist_name(self, artist_uri):
    if str(artist_uri.uri) == 'http://zitgist.com/music/artist/89ad4ac3-39f7-470e-963a-56509c546377':
      return 'Various Artists'
    else:
      return str(TripleStore.model.get_target(artist_uri, ns['foaf'].name))

  def GET(self):
    web.header('Content-Type', 'text/html; charset=utf-8')

    artists, albums = self.artists_albums()
    return render.albums(artists, albums)

app = web.application(urls, globals())

if __name__ == '__main__':
  app.run()
