## Requirements ##

- mutagen
- redland (with bdb support)
- redland-bindings (with python support)
- web.py

## Howto ##

First, tag all your music with picard.
Then, edit index.py to contain an accurate path to your music.
Then:

    ./index.py
    ./viewify.py

## Backup ##

    ./viewer.py
    curl http://localhost:8080/dump > backup.nt
