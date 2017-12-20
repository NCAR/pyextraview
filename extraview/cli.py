#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#Copyright (c) 2017, University Corporation for Atmospheric Research
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without 
#modification, are permitted provided that the following conditions are met:
#
#1. Redistributions of source code must retain the above copyright notice, 
#this list of conditions and the following disclaimer.
#
#2. Redistributions in binary form must reproduce the above copyright notice,
#this list of conditions and the following disclaimer in the documentation
#and/or other materials provided with the distribution.
#
#3. Neither the name of the copyright holder nor the names of its contributors
#may be used to endorse or promote products derived from this software without
#specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
#ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
#CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
#SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
#INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  import sys
import os
import sys
import json
import docopt
import requests
import re
from datetime import datetime
from datetime import timedelta
from . import extraview
from .log import vlog
import pkg_resources
from xml.etree import ElementTree
       
def connect(config_path = os.path.expandvars("$HOME/.extraview.json")):
    """ create extraview client instance """

    if 'EXTRAVIEW_CONFIG' in os.environ:
        config_path = int(os.environ['EXTRAVIEW_CONFIG'])

    with open(config_path, 'r') as f:
        config = json.loads(f.read())

    if not config:
        vlog(1, 'Unable to load config: %s' % (config_path))
        return None

    return extraview.client(config)

def dump_ticket(dump_format, xml):
    """
    Prints xml ticket into pretty format for user:

    dump_format: last, brief, detail, xml, full
    """
    def totext(arg):
        """ Gets text from XML object """
        if arg is None or arg.text is None:
            return "None"
        else:
            return arg.text
    def dump_title():
        """ Prints brief title for ticket """
        print(
            "{0: <10} {1: >15} {2: >10}/{3: <10} {4: >20} {5: >20} {6: <100}".format(
                id,
                status,
                group,
                user,
                host,
                vticket,
                desc,
        )) 
    def dump_comment(lastonly):
        parse_comment(xml.find("COMMENTS").text, "Resolver Comment")
        parse_comment(xml.find("HELP_CUSTOMER_COMMENTS").text, "User Comment")

        mkeys = list(msgs.keys())
        mkeys.sort()
        for dt in mkeys:
            for ctype, cmsgs in msgs[dt].items():
                for cmsg in cmsgs:
                    print("  %s %s: %s" % (dt, ctype, cmsg['user']))
                    for line in cmsg['text'].split("\n"):
                        print("\t%s" % (line))
                    if lastonly:
                        return

        print("  Description:")
        for line in xml.find("DESCRIPTION").text.split("\n"):
            print("\t%s" % (line)) 
    def parse_comment(cmt, ctype):
        txt   = []
        dt    = None
        user  = None
        for line in cmt.split("\n"):
            match = re.search('^(?P<date>[A-Z][a-z][a-z]\s+\d+,\s+\d{4}\s+\d+:\d+:\d+\s+(?:AM|PM))\s+(?P<user>\w+)$', line)
            if match:
                if dt:
                    #push new message on stack
                    msgs[dt][ctype].append({
                        'user': user, 
                        'text': "\n".join(txt)
                    })
                    txt = []
                    user = None
                    dt = None

                #Aug 30, 2013 4:10:58 PM jirina                                                                                                                                                                                                                           
                user = match.group('user')
                dt = datetime.strptime(match.group('date'), '%b %d, %Y %I:%M:%S %p')
                if not dt in msgs:
                    msgs[dt] = {}

                if not ctype in msgs[dt]:
                    msgs[dt][ctype] = []

            else:
                txt.append(line)
        if dt:
            #push last message on stack
            msgs[dt][ctype].append({
                'user': user, 
                'text': "\n".join(txt)
            }) 

    id      = totext(xml.find('ID'))
    status  = totext(xml.find('STATUS'))
    group   = totext(xml.find('HELP_ASSIGN_GROUP'))
    user    = totext(xml.find('ASSIGNED_TO'))
    host    = totext(xml.find('HELP_HOSTNAME_OTHER'))
    vticket = totext(xml.find('HELP_VENDOR_TICKET'))
    desc    = totext(xml.find('SHORT_DESCR'))
    msgs    = {} #messages by time
 
    if host is None:
        host = "-"
    if vticket is None:
        vticket = "-"
    
    if dump_format == "xml":
        ElementTree.dump(xml)
    elif dump_format == "brief":
        dump_title()
    elif dump_format == "full":
        dump_title()
        dump_comment(False)
    elif dump_format == "last":
        dump_title()
        dump_comment(True)
    elif dump_format == "detail":
        for child in xml:
            if child.text:
                for line in child.text.split("\n"):
                    print("%s: %s" % (child.tag, line))

def view():
    """
    View Extraview Ticket

    Usage:
        ev_view ID...
        ev_view [-b | --brief | -l | --last | -d | --detail | -x | --xml | -f | --full] ID...
        ev_view (-h | --help)

    Arguments:
        ID              ID of Extraview ticket (or comma delimited IDs)

    Options:
        -h, --help
        -f, --full      Print generally most useful information in ticket 
        -d, --detail    Print all known content of Extraivew ticket
        -b, --brief     Print very brief description of ticket
        -l, --last      Print last update to ticket
        -x, --xml       Print xml content of ticket
    """ 
    args = docopt.docopt(view.__doc__)
    ret = 0

    EV = connect()
    for lid in args['ID']:
        for id in lid.split(','):
            result = EV.get_issue(id)

            if result:
                if args['--xml']:
                    dump_ticket('xml', result)
                elif args['--brief']:
                    dump_ticket('brief', result)
                elif args['--detail']:
                    dump_ticket('detail', result)
                elif args['--full']:
                    dump_ticket('full', result)
                elif args['--last']:
                    dump_ticket('last', result)
                else:
                    dump_ticket('brief', result)
            else:
                vlog(1, 'Error getting ticket %s' % (id))
                ret += 1
    sys.exit(ret)


#/ssg/bin/ev_search {group|} {user|} {keyword|} {status [Assigned|Transferred|Stalled|Closed]}

def search():
    """
    Search Extraview Tickets

    Usage:
        ev_search [-b | --brief | -l | --last | -d | --detail | -x | --xml | -f | --full] GROUP [USER] [KEYWORD] [STATUS]
        ev_search (-b | --brief | -l | --last | -d | --detail | -x | --xml | -f | --full) [-g GROUP | --group GROUP] [-u USER | --user USER] [-k KEYWORD | --keyword KEYWORD] [-s STATUS | --status STATUS] [-m MAX | --max MAX] [--days DAYS]
        ev_search (-h | --help)

    Arguments:
        GROUP           Search for tickets assigned to this group
        USER            Search for tickets assigned to this user
        KEYWORD         Search for any ticket with this keyword
        STATUS          Search for any ticket with this status. Can be Assigned, Transferred, Stalled, or Closed.

    Options:
        -h, --help
        -g, --group     Search for tickets assigned to this group
        -u, --user      Search for tickets assigned to this user
        -k, --keyword   Search for any ticket with this keyword.
        -s, --status    Can be Assigned, Transferred, Stalled, Closed, or All.
        -m, --max       Maxium number of tickets to search against (Default: 200)
        --days          Maxium number of days to search against ticket open date (Default: 365 days)
        -f, --full      Print generally most useful information in ticket
        -d, --detail    Print all known content of Extraivew ticket
        -b, --brief     Print very brief description of ticket
        -l, --last      Print last update to ticket
        -x, --xml       Print xml content of ticket
    """
    args = docopt.docopt(search.__doc__)
    ret = 0
    found = 0

    EV = connect()
    max_tickets = 200
    max_days = 365
    fields = { }

    if args['MAX']:
        max_tickets= int(args['MAX'])
    if args['DAYS']:
        max_days  = int(args['DAYS'])
    if args['GROUP']:
        fields['*HELP_ASSIGN_GROUP'] = args['GROUP']
    if args['USER']:
        fields['*ASSIGNED_TO'] = args['USER']
    if args['KEYWORD']:
        fields['keyword'] = args['KEYWORD']
    if args['STATUS']:
        fields['*STATUS'] = args['STATUS']
    if args['STATUS'] is None:
        fields['STATUS'] = "STALLED;TRANSFERRED;ASSIGNED"

    fields['date'] = '-%s' % (datetime.isoformat( datetime.today() - timedelta(days=1) ))


    result = EV.search(fields, max_tickets)
    for ticket in result.iterfind('PROBLEM_RECORD'):
        found += 1
        if args['--xml']:
            dump_ticket('xml', ticket)
        elif args['--brief']:
            dump_ticket('brief', ticket)
        elif args['--detail']:
            dump_ticket('detail', ticket)
        elif args['--full']:
            dump_ticket('full', ticket)
        elif args['--last']:
            dump_ticket('last', ticket)
        else:
            dump_ticket('brief', ticket)


    if not found:
        ElementTree.dump(result)
        vlog(1, 'Nothing found.')
        ret += 1
   
    sys.exit(ret)

 
def comment():
    """
    Add Resolver Comment to Extraview Ticket

    Usage:
        ev_comment ID COMMENT
        ev_comment (-i ID | --id ID) (-c COMMENT | --comment COMMENT) 
        ev_comment (-h | --help)

    Arguments:
        ID              ID of Extraview ticket (or comma delimited IDs)
        COMMENT         Resolver comment to add to ticket

    Options:
        -h, --help
    """ 
    args = docopt.docopt(comment.__doc__)
    ret = 0

    EV = connect()
    for id in args['ID'].split(','):
        result = EV.add_resolver_comment( id, args['COMMENT'])

        vlog(4, 'Result: %s %s' % (result.status_code, result.text))
        if result.status_code == requests.codes.ok and result.text.find("Exception") == -1:
            vlog(2, 'Added comment to %s' % (id))
        else:
            vlog(1, 'Error code %s:\n%s' % (result.status_code, result.text))
            ret += 1
    sys.exit(ret)
 
def assign():
    """
    Assign Extraview Ticket

    Usage:
        ev_assign ID GROUP [USER] [COMMENT] [PRIORITY]
        ev_assign (-i ID | --id ID) [-c COMMENT | --comment COMMENT] (-g GROUP | --group GROUP) [-u USER | --user USER] [-p PRIORITY | --priority PRIORITY]
        ev_assign (-h | --help)

    Arguments:
        ID              ID of Extraview ticket (or comma delimited IDs)
        GROUP           Assign group to ticket
        USER            Assign user to ticket
        PRIORITY        Assign priority to ticket
        COMMENT         Comment to user while assigning ticket

    Options:
        -h, --help
    """ 
    args = docopt.docopt(assign.__doc__)
    ret = 0

    EV = connect()
    for id in args['ID'].split(','):
        fields = {}
        if args['PRIORITY']:
            fields['*PRIORITY'] = args['PRIORITY']
        if args['COMMENT']:
            fields['COMMENTS'] = args['COMMENT']
         
        result = EV.assign_group( id, args['GROUP'], args['USER'], fields)

        vlog(4, 'Result: %s %s' % (result.status_code, result.text))
        if result.status_code == requests.codes.ok and result.text.find("Exception") == -1:
            vlog(2, 'Assigned %s' % (id))
        else:
            vlog(1, 'Error code %s:\n%s' % (result.status_code, result.text))
            ret += 1
    sys.exit(ret)
 
def close():
    """
    Close Extraview Ticket

    Usage:
        ev_close ID [COMMENT]
        ev_close (-i ID | --id ID) (-c COMMENT | --comment COMMENT)
        ev_close (-h | --help)

    Arguments:
        ID              ID of Extraview ticket (or comma delimited IDs)
        COMMENT         Comment to user while closing

    Options:
        -h, --help
    """ 
    args = docopt.docopt(close.__doc__)
    ret = 0

    EV = connect()
    for id in args['ID'].split(','):
        result = EV.close( id, args['COMMENT'] )

        if result.status_code == requests.codes.ok and result.text.find("Exception") == -1:
            vlog(2, 'Closed %s' % (id))
        else:
            vlog(1, 'Error code %s:\n%s' % (result.status_code, result.text))
            ret += 1
    sys.exit(ret)

def create():
    """
    Create Extraview Ticket

    Usage:
        ev_create ORIGINATOR GROUP USER TITLE DESCRIPTION [PRIORITY]
        ev_create (-u USER | --user USER) (-g GROUP | --group GROUP) (-t TITLE | --title TITLE) (-d DESCRIPTION | --description DESCRIPTION | --desc DESCRIPTION) [-p PRIORITY | --priority PRIORITY]
        ev_create (-h | --help)

    Arguments:
        ORIGINATOR      Originating user for ticket
        GROUP           Assigned group for ticket
        USER            Assigned user for ticket
        TITLE           Title of new ticket
        DESCRIPTION     Desciption of new ticket
        PRIORITY        Priority of new ticket

    Options:
        -h, --help
    """ 
    args = docopt.docopt(create.__doc__)

    fields = {}
    if args['PRIORITY']:
        fields['*PRIORITY'] = args['PRIORITY']

    result = connect().create(
        args['ORIGINATOR'],
        args['GROUP'],
        args['USER'],
        args['TITLE'],
        args['DESCRIPTION'],
        fields
    )

    if result:
        vlog(2, result)
        sys.exit(0)
    else:
        sys.exit(1)
        
