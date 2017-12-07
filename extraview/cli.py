#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import os
import json
from . import extraview
from .log import vlog
       
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

