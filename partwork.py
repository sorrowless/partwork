# coding=utf-8
__author__ = 'gra2f'

import os

from fileslist import getfiles
from fileprocessing import gettags,getartwork,setartwork
import lastfmcheck as lfm
import localcheck as lchk

def getmp3():
  '''Parse command-line and do all work to find files to artwork and all calls to
     treat with them'''
  for file in getfiles():
    # if file already artworked - skip
    if lchk.isFileArtworked(file):
      print('file %s already artworked' % file)
      continue

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


if __name__ == "__main__":
    getmp3()
    # TODO: optionally, we can save downloaded artwork in local directory (but we need to smart save - e.g.
    # do not save cover in directory with many files from different albums)
    # TODO: we can do 'smart' find - e.g. if files from one album locate in one directory, then we don't need to find
    # picture for them many times - only first time is enough
    # TODO: add new search engines
    # TODO: print list of not artworked files after doing all work
    # TODO: verbose info
    # TODO: save unartworked files in file and add option to load that list in next time
