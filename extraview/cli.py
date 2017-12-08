#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import os
import json
import docopt
import requests
from . import extraview
from .log import vlog
import pkg_resources
       
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
          
def view():
    True  

def search():
    True

def comment():
    True

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
            sys.exit(0)
        else:
            vlog(1, 'Error code %s:\n%s' % (result.status_code, result.text))
            sys.exit(1)
 
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

    EV = connect()
    for id in args['ID'].split(','):
        result = EV.close( id, args['COMMENT'] )

        vlog(4, 'Result: %s %s' % (result.status_code, result.text))
        if result.status_code == requests.codes.ok and result.text.find("Exception") == -1:
            vlog(2, 'Closed %s' % (id))
            sys.exit(0)
        else:
            vlog(1, 'Error code %s:\n%s' % (result.status_code, result.text))
            sys.exit(1)
 
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
        
