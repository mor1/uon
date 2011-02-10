#!/usr/bin/env python2.7
#
# Webscrape SaturnWeb for module registrations.
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

import sys, getopt, urllib, scraper, pprint, json

LOGIN_FORM = 'https://saturnweb.nottingham.ac.uk/Nottingham/asp/logon_saturn_frame.asp' 
LOGIN_CONFIRM = 'https://saturnweb.nottingham.ac.uk/Nottingham/asp/logon.asp' 
SEARCH_URL = 'https://saturnweb.nottingham.ac.uk/Nottingham/asp/search_students.asp' 

DEFAULT_YEAR = '2010'

def die_with_usage(err="Usage: ", code=0):
    print """ERROR: %s
%s [modules]:
  -h/--help            : print this message
  -a/--ascii           : output ASCII
  -j/--json            : output JSON  

  -u/--username <u>    : SaturnWeb username <u>
  -p/--password <p>    : SaturnWeb password <p>
  -y/--year <y>        : Year (2010, 2011, ...; default:%s)
    """ % (err, sys.argv[0], DEFAULT_YEAR)
    sys.exit(code)

def login(username, password):
    _, h = scraper.fetch(LOGIN_FORM, data={'UserName': username,
                                           'Password': password,
                                           'SUBMIT1': 'Login',
                                           })
    if 'set-cookie' not in h: BARF
    cookies = h['set-cookie']
    scraper.fetch(LOGIN_CONFIRM, headers={'Cookie': cookies,})

    return cookies

def scrape_register(cookies, module, year_id):
    page, _ = scraper.fetch(
        "%s?%s" % (SEARCH_URL, urllib.urlencode({ 'form_id': 3,
                                                  'exclude': '',
                                                  'year_id': year_id,
                                                  'mnem': module,
                                                  })),
        headers={'Cookie': cookies,}
        )

    doc = scraper.parse(page)
##     print page
    title = doc.find(scraper.path("h4", "a")).text

    for table in doc.findall(scraper.path("table")):
        if 'bordercolor' in table.keys():
            headings = [ t.text for t in table.findall(scraper.path("th", "font", "b")) ]
            if headings != [ 'Name', 'Category', 'Course', 'Misc' ]: BARF

##             for row in table.findall(scraper.path("tr"))[1:]:
##                 for c in row.findall(scraper.path("td", "font")):
##                     print c, c.text, c.tail

            students = [
                dict(zip(headings[:-1],
                         (c.text.strip()
                          for c in row.findall(scraper.path("td", "font"))
                          if c.text)))
                for row in table.findall(scraper.path("tr"))[1:]
                ]

            return {
                'title': title,
                'students': students,
                }
        
if __name__ == '__main__':

    YID = {
        '2012': '000112',
        '2011': '000111',
        '2010': '000110',
        '2009': '000109',
        }
    
    ## option parsing
    pairs = [ "h/help", "j/json", "a/ascii",
              "u:/username=", "p:/password=", "y:/year_id=",
              ]
    shortopts = "".join([ pair.split("/")[0] for pair in pairs ])
    longopts = [ pair.split("/")[1] for pair in pairs ]
    try: opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError, err: die_with_usage(err, 2)

    dump_json = False
    dump_ascii = False
    username = password = None
    modules = year_id = None
    try:
        for o, a in opts:
            if o in ("-h", "--help"): die_with_usage()
            elif o in ("-a", "--ascii"): dump_ascii = True
            elif o in ("-j", "--json"): dump_json = True
            elif o in ("-u", "--username"): username = a
            elif o in ("-p", "--password"): password = a
            elif o in ("-y", "--year"): year_id = YID[a]
            else: raise Exception("unhandled option")
    except Exception, err: raise ; die_with_usage()

    modules = args
    if not (username and password): die_with_usage("must supply username and password", 1)
    if not modules: die_with_usage("must specific module mnemonic(s)", 2)
    if not year_id: year_id = YID[DEFAULT_YEAR]
    if not (dump_ascii or dump_json): dump_ascii = True

    cookies = login(username, password)
    for module in modules:
        register = scrape_register(cookies, module, year_id)
        if dump_json: print json.dumps(register)
        elif dump_ascii:
            print "\x1b[0;1m%s\x1b[0m [%d]" % (register['title'], len(register['students']))
            for s in register['students']:
                print "\t", "\t".join(s.values())
