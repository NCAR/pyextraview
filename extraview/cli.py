#!/usr/bin/python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import json
import docopt
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
 
def close():
    """Usage: ev_close [-h | --help] (ODD EVEN)...
    Example, try:
      odd_even_example.py 1 2 3 4
    Options:
      -h, --help
    """ 
    args = docopt.docopt(close.__doc__)
    print(args)

def create():
    """Usage: ev_create [-h | --help] (ODD EVEN)...
    Example, try:
      odd_even_example.py 1 2 3 4
    Options:
      -h, --help
    """ 
    args = docopt.docopt(create.__doc__)
    print(args)

