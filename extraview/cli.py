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

    return extraview.client(config)

