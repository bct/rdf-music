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

import TripleStore
from Vocab import ns

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

def state_audio_metadata(ts, filename, metadata):
  # it doesn't matter if we add the same statement multiple times, so don't
  # bother checking if it exists (this could cause problems if we have eg.
  # different artist names with the same musicbrainz_artistid

  # artist
  artist_uri = 'http://zitgist.com/music/artist/' + metadata['musicbrainz_artistid'][0]
  artist_uri = RDF.Node(RDF.Uri(artist_uri))

  ts.state(artist_uri, ns['rdf'].type, ns['mo'].MusicArtist)
  ts.state(artist_uri, ns['foaf'].name, RDF.Node(metadata['artist'][0]))

  # album
  album_uri = 'http://zitgist.com/music/record/' + metadata['musicbrainz_albumid'][0]
  album_uri = RDF.Node(RDF.Uri(album_uri))

  ts.state(album_uri, ns['rdf'].type, ns['mo'].Record)
  # XXX does album artist have an MO term?
  ts.state(album_uri, ns['foaf'].maker, artist_uri)
  # XXX use dc:title here?
  ts.state(album_uri, ns['dc'].title, RDF.Node(metadata['album'][0]))

  # track
  track_uri = 'http://zitgist.com/music/track/' + metadata['musicbrainz_trackid'][0]
  track_uri = RDF.Node(RDF.Uri(track_uri))

  ts.state(track_uri, ns['rdf'].type, ns['mo'].Track)
  # XXX use dc:title here?
  ts.state(track_uri, ns['dc'].title, RDF.Node(metadata['title'][0]))

  tn = RDF.Node(literal=metadata['tracknumber'][0], datatype=ns['xs'].int.uri)
  ts.state(track_uri, ns['mo'].track_number, tn)
  ts.state(track_uri, ns['foaf'].maker, artist_uri)

  # the particular file
  file_uri = 'file://' + filename
  file_uri = RDF.Node(RDF.Uri(file_uri))

  ts.state(file_uri, ns['mo'].encodes, track_uri)

if __name__ == '__main__':
  for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
      file = os.path.join(dirpath, name)
      metadata = get_audio_metadata(file)
      state_audio_metadata(TripleStore, file, metadata)

  print '---'

  for statement in TripleStore.model:
    print statement
