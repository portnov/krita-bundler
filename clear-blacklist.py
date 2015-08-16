#!/usr/bin/env python

import os
from os.path import expanduser
import argparse
from lxml import etree

def parse_cmdline():
    parser = argparse.ArgumentParser(description='Remove blacklisted resources')
    parser.add_argument('-f', '--force', action='store_true', help='Actually remove files. Without this flag - just list them.')
    parser.add_argument('filename', metavar='FILENAME.blacklist', help='*.blacklist file')
    return parser.parse_args()

args = parse_cmdline()
xml = etree.fromstring(open(args.filename).read())

for e in xml.findall('file/name'):
    path = expanduser(e.text)
    if path.startswith('bundle://'):
        continue
    if args.force:
        os.remove(path)
    else:
        print("rm " + path)

