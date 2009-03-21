#!/usr/bin/env python

'''
Recursively indexes a directory of music files (mp3, ogg, flac) and watches
for changes.
'''

path = '/home/data/thingy/music'

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
  ext = os.path.splitext(filename)[1].lower()
  if ext == '.mp3':
    file = ID3(filename)

    dict = {}

    dict['musicbrainz_trackid'] = [file['UFID:http://musicbrainz.org'].data]
    dict['tracknumber'] = [file['TRCK'].text[0].split('/')[0]]
    dict['title'] = file['TIT2'].text

    dict['musicbrainz_artistid'] = file['TXXX:MusicBrainz Artist Id'].text
    dict['artist'] = file['TPE1'].text

    if 'TXXX:MusicBrainz Album Artist Id' in file:
      dict['musicbrainz_albumartistid'] = file['TXXX:MusicBrainz Album Artist Id'].text

    # ignore TPE2 (which MB uses for album artist name), it's rarely there
    # and it's being misused anyhow

    dict['musicbrainz_albumid'] = file['TXXX:MusicBrainz Album Id'].text
    dict['album'] = file['TALB'].text

  # sane formats already have standardized field names
  elif ext == '.ogg':
    dict = OggVorbis(filename)
  elif ext == '.flac':
    dict = FLAC(filename)

  return dict

def state_audio_metadata(ts, file_uri, metadata):
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
  ts.state(album_uri, ns['dc'].title, RDF.Node(metadata['album'][0]))

  if 'musicbrainz_albumartistid' in metadata:
    album_artist_uri = 'http://zitgist.com/music/artist/' + metadata['musicbrainz_albumartistid'][0]
    album_artist_uri = RDF.Node(RDF.Uri(album_artist_uri))
  else:
    album_artist_uri = artist_uri

  # XXX does album artist have an MO term?
  ts.state(album_uri, ns['foaf'].maker, album_artist_uri)

  # track
  track_uri = 'http://zitgist.com/music/track/' + metadata['musicbrainz_trackid'][0]
  track_uri = RDF.Node(RDF.Uri(track_uri))

  ts.state(track_uri, ns['rdf'].type, ns['mo'].Track)
  ts.state(album_uri, ns['mo'].track, track_uri)

  ts.state(track_uri, ns['foaf'].maker, artist_uri)
  ts.state(track_uri, ns['dc'].title, RDF.Node(metadata['title'][0]))

  # some artists get clever and have craaaaazzy track numbers
  if 'tracknumber' in metadata:
    tn = metadata['tracknumber'][0]
  else:
    tn = '0'

  tn = RDF.Node(literal=tn, datatype=ns['xs'].int.uri)
  ts.state(track_uri, ns['mo'].track_number, tn)

  # the particular file
  ts.state(file_uri, ns['mo'].encodes, track_uri)

if __name__ == '__main__':
  for dirpath, dirnames, filenames in os.walk(path):
    for filename in filenames:
      abs_path = os.path.join(dirpath, filename) # full path

      metadata = get_audio_metadata(abs_path)
      if not metadata:
        print 'could not extract metadata, skipping', abs_path
        continue

      file_uri = 'file://' + abs_path
      file_uri = RDF.Node(RDF.Uri(file_uri))

      track_uri = 'http://zitgist.com/music/track/' + metadata['musicbrainz_trackid'][0]
      track_uri = RDF.Node(RDF.Uri(track_uri))

      # don't restate files that we already had
      st = RDF.Statement(file_uri, ns['mo'].encodes, track_uri)
      if TripleStore.model.contains_statement(st):
        print 'already had', metadata['title'][0]
        continue

      state_audio_metadata(TripleStore, file_uri, metadata)

  print '---'

  for statement in TripleStore.model:
    print statement
