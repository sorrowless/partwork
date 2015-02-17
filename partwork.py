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
    # lastFM check
    tags = gettags(file)
    url = lfm.process(*tags)
    tempArtFile = getartwork(url)
    if tempArtFile:
      setartwork(file, localCover)
      continue

  # TODO: optionally, we can save downloaded artwork in local directory (but we need to smart save - e.g.
  # do not save cover in directory with many files from different albums)
  # TODO: we can do 'smart' find - e.g. if files from one album locate in one directory, then we don't need to find
  # picture for them many times - only first time is enough
  # TODO: add new search engines
  # TODO: print list of not artworked files after doing all work
  # TODO: verbose info
    # TODO: save unartworked files in file and add option to load that list in next time
