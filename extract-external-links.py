#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
from extractor import KPP

for fname in sys.argv[1:]:
    print("Processing: {}".format(fname))
    kpp = KPP(fname)

    links = kpp.get_links()
    for name, value in links.iteritems():
        print("{}: {}".format(name, value))

