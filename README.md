# pyextraview
This python module provides an wrapper API to query an existing Extraview server. 

Requirements:
* A user be setup on the Extraview server, usually in the resolver role.
  * Sockets connectivity to Extraview server API (usually in /evj/ExtraView/ev_api.action on the webserver).
* Python3
* [PIP](https://pypi.python.org/pypi/pip)
* make

Tools Provided:
* ev_assign
  * Assigns tickets to users, groups while allowing comments to be provided.
* ev_close
  * Closes tickets.
* ev_comment
  * Add resolver comment to a given ticket or group of tickets.
* ev_create
  * Creates tickets based on json configuration.
* ev_search
  * Search tickets for given fields.
* ev_view
  * View specific tickets in multiple formats.
  
Setup:
1. Clone the repo
  ```bash
  user@host# git clone https://github.com/NCAR/pyextraview.git
  ```
2. Call make to install 
  ```bash
  user@host# make
  ```
3. Add Extraview configuration 
  ```bash
  user@host# cp contrib/extraview.json ~/extraview.json
  user@host# vim ~/extraview.json
  ```
