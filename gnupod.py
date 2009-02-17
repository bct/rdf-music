import RDF
import TripleStore
import Vocab

import subprocess

def add_album(album):
  '''this can only be called once at a time!'''
  album = RDF.Node(RDF.Uri(album))

  cmd = ['gnupod_addsong.pl', '--decode=mp3']

  for track in TripleStore.model.get_targets(album, Vocab.ns['mo'].track):
    cmd.append(track_filename(track))

  artist = TripleStore.model.get_target(album, Vocab.ns['foaf'].maker)
  for tag in Vocab.tags(artist):
    cmd += ['-p', tag]

  for tag in Vocab.tags(album):
    cmd += ['-p', tag]

  subprocess.call(cmd)
