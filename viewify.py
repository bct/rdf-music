#!/usr/bin/env python

import web

urls = (
  '/', 'index',
  '/tag', 'tag',
  '/rate', 'rate',
)

import RDF
import TripleStore

from Vocab import ns

def rating(resource):
  rating = TripleStore.model.get_target(resource, ns['nao'].numericRating)

  if rating is None:
    return 0

  return int(rating.literal_value['string']) / 2

template_globals = {'rating': rating}
render = web.template.render('templates/', globals=template_globals)

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

  def tags(self, resource):
    for tag in TripleStore.model.get_targets(resource, ns['nao'].hasTag):
      name = str(TripleStore.model.get_target(tag, ns['nao'].prefLabel))
      yield name

  def artist_tags(self, artists):
    '''a dict with artists' tags, keyed by artist URI'''

    tags = {}

    for name, artist_uri in artists:
      tags[artist_uri] = self.tags(artist_uri)

    return tags

  def GET(self):
    web.header('Content-Type', 'text/html; charset=utf-8')

    artists, albums = self.artists_albums()
    artist_tags = self.artist_tags(artists)

    return render.albums(artists, albums, artist_tags)

class tag:
  '''tag a resource using nao'''

  def tag(self, resource, tags):
    resource = RDF.Node(RDF.Uri(resource))
    # space-separated, remove empty
    tags = [x for x in tags.strip().split(' ') if x != '']

    # remove all existing tags on this resource
    TripleStore.forget(resource, ns['nao'].hasTag, None)

    for _tag in tags:
      # XXX check if it's a nao:Tag too
      tag = TripleStore.model.get_source(ns['nao'].prefLabel, RDF.Node(_tag))

      if not tag:
        # create a new nao:Tag with the appropriate prefLabel
        tag = RDF.Node(blank=None)
        TripleStore.state(tag, ns['rdf'].type, ns['nao'].Tag)
        TripleStore.state(tag, ns['nao'].prefLabel, RDF.Node(_tag))

      TripleStore.state(resource, ns['nao'].hasTag, tag)

  def POST(self):
    i = web.input()

    self.tag(i.uri, i.tags)

class rate:
  '''rate a resource using nao'''

  def rate(self, resource, rating):
    resource = RDF.Node(RDF.Uri(resource))

    rating = str(int(rating) * 2)
    rating = RDF.Node(literal=rating, datatype=ns['xs'].float.uri)

    # delete any existing ratings for this resource
    TripleStore.forget(resource, ns['nao'].numericRating, None)

    TripleStore.state(resource, ns['nao'].numericRating, rating)

  def POST(self):
    i = web.input()
    self.rate(i.uri, i.rating)

app = web.application(urls, globals())

if __name__ == '__main__':
  app.run()

  print 'a'
  TripleStore.model.sync()
  print 'b'
