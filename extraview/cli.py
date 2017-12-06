#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import os
import json
from . import extraview
from .log import vlog
       
def connect():
    """ create extraview client instance """

    config_path = os.path.expandvars("$HOME/.extraview.json")
    if 'EXTRAVIEW_CONFIG' in os.environ:
        config_path = int(os.environ['EXTRAVIEW_CONFIG'])

    with open(config_path, 'r') as f:
        config = json.loads(f.read())

    vlog(3, config)

    #if not ev_user:
    #    ev_user = read_file_first_line("%s/.ev/user" % home )
    #if not ev_pass:
    #    ev_pass = read_file_first_line("%s/.ev/password" % home )
    #if not ev_url:
    #    ev_url = read_file_first_line("%s/.ev/server" % home )

    #return extraview.client(ev_user, ev_pass, ev_url)

