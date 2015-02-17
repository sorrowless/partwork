# coding=utf-8
__author__ = 'gra2f'

import os
import argparse
import logging
import sys

from fileslist import getfiles
from fileprocessing import gettags,getartwork,setartwork
import lastfmcheck as lfm
import localcheck as lchk


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--file', nargs = '+')
  parser.add_argument('-d', '--dir', nargs = '+')
  parser.add_argument('-r', '--recursive', action = 'store_true')
  parser.add_argument('-v', '--verbosity', action = 'count')
  args = parser.parse_args(sys.argv[1:])

  if not args.verbosity:
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
  elif args.verbosity == 1:
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.info("Verbosity enabled")
  elif args.verbosity > 1:
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.debug("Debug enabled")

  cached = { 'artist':'', 'album':'', 'path':'' }

  for file in getfiles(file=args.file,directory=args.dir,recursive=args.recursive):
    # if file already artworked - skip
    if lchk.isFileArtworked(file):
      logging.info('File %s already artworked\n' % file)
      continue

    print("File is: %s" % file)
    # if local cover in filedir exists - set and go to next file
    localCover = lchk.isLocalCovers(os.path.dirname(os.path.abspath(file)))
    if localCover:
      setartwork(file, localCover)
      continue

    # process with outside sources
    tags = gettags(file)
    # check that we have something at all
    if tags[0] == False and tags[1] == False:
      logging.warn('We don\'t have anything about that file, so it\'s nothing to find\n')
      continue

    # then check cache first
    if cached['artist'] == tags[0] and cached['album'] == tags[1]:
      if cached['path']:
        logging.info('Local cache found, using it')
        setartwork(file, cached['path'])
        continue
      else:
        logging.warn('Artist and album found in local cache, but artwork not found. It doesn\'t have sense to try find it again\n')
        continue
    else:
      cached['artist'],cached['album'] = tags
      cached['path'] = ''

    # lastFM check
    url = lfm.process(*tags)
    tempArtFile = getartwork(url)
    if tempArtFile:
      cached['path'] = tempArtFile
      setartwork(file, tempArtFile)
      continue

  # TODO: optionally, we can save downloaded artwork in local directory (but we need to smart save - e.g.
  # do not save cover in directory with many files from different albums)
  # TODO: add new search engines
  # TODO: we can try to get tags harder - e.g., from local name, from some sources like shazam etc.
  # TODO: print list of not artworked files after doing all work
  # TODO: verbose info
    # TODO: save unartworked files in file and add option to load that list in next time
