#!/usr/bin/env python

'''
Recursively indexes a directory of music files (mp3, ogg, flac) and watches
for changes.
'''

import os

from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.id3 import ID3

path = '/home/data/music'

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

    dict['musicbrainz_trackid'] = file['TXXX:MusicBrainz Artist Id'].text
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

if __name__ == '__main__':
  for dirpath, dirnames, filenames in os.walk(path):
    for name in filenames:
      file = os.path.join(dirpath, name)
      print get_audio_metadata(file)
