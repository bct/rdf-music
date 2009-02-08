#!/usr/bin/env python

'''
Recursively indexes a directory of music files (mp3, ogg, flac) and watches
for changes.
'''

path = '/home/data/music'

import os

from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.id3 import ID3

import RDF
storage = RDF.HashStorage('music', options="hash-type='bdb'")
model = RDF.Model(storage)

def get_audio_metadata(filename):
  '''take a path to a music file, grab the metadata with mutagen
return a standardized dict, or None if it's not an audio file or there's no
MusicBrainz data

output fields defined at <http://wiki.musicbrainz.org/PicardTagMapping>
'''

  dict = None

  #   doing this based on extension is wrong
  # ~* filetype is metadata, no gods no masters *~
  ext = os.path.splitext(name)[1]
  if ext == '.mp3':
    file = ID3(filename)

    dict = {}

    dict['musicbrainz_trackid'] = [file['UFID:http://musicbrainz.org'].data]
    dict['tracknumber'] = [file['TRCK'].text[0].split('/')[0]]
    dict['title'] = file['TIT2'].text

    dict['musicbrainz_artistid'] = file['TXXX:MusicBrainz Artist Id'].text
    dict['artist'] = file['TPE1'].text

    dict['musicbrainz_albumartistid'] = file['TXXX:MusicBrainz Album Artist Id'].text
    dict['albumartist'] = file['TPE2'].text

    dict['musicbrainz_albumid'] = file['TXXX:MusicBrainz Album Id'].text
    dict['album'] = file['TALB'].text

  # sane formats already have standardized field names
  elif ext == '.ogg':
    dict = OggVorbis(filename)
  elif ext == '.flac':
    dict = FLAC(filename)

  return dict


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

def state_audio_metadata(filename, metadata):
  # it doesn't matter if we add the same statement multiple times, so don't
  # bother checking if it exists (this could cause problems if we have eg.
  # different artist names with the same musicbrainz_artistid

  # artist
  artist_uri = 'http://zitgist.com/music/artist/' + metadata['musicbrainz_artistid'][0]
  artist_uri = RDF.Node(RDF.Uri(artist_uri))

  st = RDF.Statement(artist_uri, ns['rdf'].type, ns['mo'].MusicArtist)
  model.append(st)

  st = RDF.Statement(artist_uri, ns['foaf'].name, RDF.Node(metadata['artist'][0]))
  model.append(st)

  # album
  album_uri = 'http://zitgist.com/music/record/' + metadata['musicbrainz_albumid'][0]
  album_uri = RDF.Node(RDF.Uri(album_uri))

  st = RDF.Statement(album_uri, ns['rdf'].type, ns['mo'].Record)
  model.append(st)

  # XXX does album artist have an MO term?
  st = RDF.Statement(album_uri, ns['foaf'].maker, artist_uri)
  model.append(st)

  # XXX use dc:title here?
  st = RDF.Statement(album_uri, ns['dc'].title, RDF.Node(metadata['album'][0]))
  model.append(st)

  # track
  track_uri = 'http://zitgist.com/music/track/' + metadata['musicbrainz_trackid'][0]
  track_uri = RDF.Node(RDF.Uri(track_uri))

  st = RDF.Statement(track_uri, ns['rdf'].type, ns['mo'].Track)
  model.append(st)

  # XXX use dc:title here?
  st = RDF.Statement(track_uri, ns['dc'].title, RDF.Node(metadata['title'][0]))
  model.append(st)

  st = RDF.Statement(track_uri, ns['mo'].track_number, RDF.Node(literal=metadata['tracknumber'][0], datatype=ns['xs'].int.uri))
  model.append(st)

  st = RDF.Statement(track_uri, ns['foaf'].maker, artist_uri)
  model.append(st)

if __name__ == '__main__':
  for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
      file = os.path.join(dirpath, name)
      metadata = get_audio_metadata(file)
      state_audio_metadata(file, metadata)

  print '---'

  for statement in model:
    print statement
