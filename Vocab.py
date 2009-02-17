import RDF

ns = {
  'dc': RDF.NS('http://purl.org/dc/elements/1.1/'),
  'foaf': RDF.NS('http://xmlns.com/foaf/0.1/'),
  'frbr': RDF.NS('http://purl.org/vocab/frbr/core#'),
  'rdf': RDF.NS('http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
  'nao': RDF.NS('http://www.semanticdesktop.org/ontologies/2007/08/15/nao#'),
  # original URL has been removed (MusicBrainz noooooo :()
  # described at <http://www.schemaweb.info/schema/SchemaInfo.aspx?id=168>
  'mm': RDF.NS('http://musicbrainz.org/mm/mm-2.1#'),
  'mo': RDF.NS('http://purl.org/ontology/mo/'),
  # need this to get xs:int track_numbers working
  'xs': RDF.NS('http://www.w3.org/2001/XMLSchema#'),
}

import TripleStore

def rating(resource):
  '''a resource's nao:numericRating'''
  rating = TripleStore.model.get_target(resource, ns['nao'].numericRating)

  if rating is None:
    return 0

  return int(rating.literal_value['string'])

def rate(resource, rating):
  '''give a resource a nao:numericRating (float from 1-10)'''
  resource = RDF.Node(RDF.Uri(resource))

  rating = RDF.Node(literal=str(rating), datatype=ns['xs'].float.uri)

  # delete any existing ratings for this resource
  TripleStore.forget(resource, ns['nao'].numericRating, None)

  TripleStore.state(resource, ns['nao'].numericRating, rating)

def tags(resource):
  '''the nao:prefLabels of a resource's nao:hasTags'''
  for tag in TripleStore.model.get_targets(resource, ns['nao'].hasTag):
    name = str(TripleStore.model.get_target(tag, ns['nao'].prefLabel))
    yield name

def tag(resource, tags):
  '''tag a resource with a space-separated string'''
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

def track_filename(track):
  filename = str(TripleStore.model.get_source(ns['mo'].encodes, track).uri)
  # strip the file:// scheme prefix
  return filename[7:]

def artist_name(artist_uri):
  if str(artist_uri.uri) == 'http://zitgist.com/music/artist/89ad4ac3-39f7-470e-963a-56509c546377':
    return 'Various Artists'
  else:
    return str(TripleStore.model.get_target(artist_uri, ns['foaf'].name))

def artists_albums():
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
    name = artist_name(artist_uri)
    artists.append((name, artist_uri,))

  artists.sort()

  return (artists, albums)

