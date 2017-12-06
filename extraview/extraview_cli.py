#!/usr/bin/python
import extraview
import os
from nfile import read_file_first_line
       
def open_extraview(ev_user = None, ev_pass = None, ev_url = None):
    """ create extraview client """
    home = os.getenv("HOME")
    if not ev_user:
	ev_user = read_file_first_line("%s/.ev/user" % home )
    if not ev_pass:
	ev_pass = read_file_first_line("%s/.ev/password" % home )
    if not ev_url:
	ev_url = read_file_first_line("%s/.ev/server" % home )

    return extraview.client(ev_user, ev_pass, ev_url)

