#!/usr/bin/env python

import web

urls = (
  '/', 'index',
  '/tag', 'tag',
  '/tag/(.*)', 'taggedalbums',
  '/rate', 'rate',
  '/ipod', 'ipod',
  '/dump', 'dump',
)

import RDF
import TripleStore

import Vocab
from Vocab import ns

# modify this if you're mounting somewhere other than the root
# XXX should be configurable, along with index.py's search path(s)
def url(path):
  return '/' + path

template_globals = {'rating': Vocab.rating, 'tags': Vocab.tags, 'url': url}
render = web.template.render('templates/', globals=template_globals)

import gnupod

class index:
  def GET(self):
    web.header('Content-Type', 'text/html; charset=utf-8')

    artists, albums = Vocab.artists_albums()

    return render.albums(artists, albums)

class tag:
  '''tag a resource using nao'''

  def POST(self):
    i = web.input()

    Vocab.tag(i.uri, i.tags)

class taggedalbums:
  '''albums tagged with a certain label'''

  def GET(self, tag):
    artists, albums = Vocab.artists_albums_tagged(tag)

    return render.tagged(tag, artists, albums)

class rate:
  '''rate a resource using nao'''

  def POST(self):
    i = web.input()
    Vocab.rate(i.uri, int(i.rating)*2)

class ipod:
  '''manage moving tracks to/from an ipod'''
  def POST(self):
    i = web.input()
    gnupod.add_album(i.album)

class dump:
  '''dump the database into NTriples'''
  def GET(self):
    sr = RDF.NTriplesSerializer()
    return sr.serialize_model_to_string(TripleStore.model)

app = web.application(urls, globals())

if __name__ == '__main__':
  app.run()
  TripleStore.model.sync()
