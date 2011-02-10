#
# Webscraper utility functions.
#
# Copyright (C) 2011 Richard Mortier <mort@cantab.net>.  All Rights
# Reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
# USA.

import urllib, urllib2
import html5lib
from html5lib import sanitizer
from html5lib import treebuilders
from xml.etree import cElementTree as et
from xml.dom import minidom

def tag(t): return "{http://www.w3.org/1999/xhtml}%s" % (t,)

def decode(bytes):
    try: page = bytes.decode("utf8")
    except UnicodeEncodeError, ue:
        try: page = bytes.encode("utf8")
        except UnicodeEncodeError, ue:
            page = bytes.encode("latin1")

    except UnicodeDecodeError, ud:
        page = bytes.decode("latin1")

    return page

def fetch(url, data=None, headers={}):
    if not data: req = urllib2.Request(url, headers=headers)
    else:
        req = urllib2.Request(url, urllib.urlencode(data), headers)
        
    f = urllib2.urlopen(req)
    headers = dict(f.info().items())
    bytes = f.read()
    ct = headers['content-type'] if ('content-type' in headers) else ""
    page = bytes.decode("latin1") if ("charset=ISO-8859-1" in ct) else decode(bytes)
    return (page, headers)

def parse(page):
    parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("etree", et),)
##                                  tokenizer=sanitizer.HTMLSanitizer)
    return parser.parse(page)

def path(*elts):
    return ".//%s" % "//".join([ tag(e) for e in elts ])
