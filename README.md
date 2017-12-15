# pyextraview
This python module provides an wrapper API to query an existing Extraview server. 

## Requirements:
* A user be setup on the Extraview server, usually in the resolver role.
  * Sockets connectivity to Extraview server API (usually in /evj/ExtraView/ev_api.action on the webserver).
* Python3
* [PIP](https://pypi.python.org/pypi/pip)
* make

## Tools Provided:
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
  
## Setup:
1. Clone the repo
  ```bash
  user@host# git clone https://github.com/NCAR/pyextraview.git
  ```
2. Call make to install 
  ```bash
  user@host# make
  ```
  * On distros where python2 is favored over python3:
    ```bash
    $ zypper install python3-setuptools #SLES
    $ easy_install-3.4 pip
    $ pip3 install -r requirements.txt 
    $ pip3 install . 
    ```
3. Add Extraview configuration 
  ```bash
  user@host# cp contrib/extraview.json ~/extraview.json
  user@host# vim ~/extraview.json
  ```
## Configuration

You will need to create a configuration file that will tell the Extraview API which server to talk to and what user to use. The configuration also allows you to set default values for fields that may be specific to your organization.

Here is the default example configuration:
```json
{
    "server": {
        "password": "{INSERT PASSWORD HERE}",
        "url": "https://{INSERT EXTRAVIEW HOSTNAME}/evj/ExtraView/ev_api.action?",
        "user": "{INSERT USER HERE}"
    },
    "create": {
            "send_email": "no",
            "REQUESTOR_NAME": "{INSERT YOUR USER NAME}",
            "*PRIORITY": "{INSERT DEFAULT PRIORITY}",
            "REQUESTOR_EMAIL": "{INSERT EMAIL}",
            "CONTACT_PHONE": "{INSERT PHONE}"
    },
    "close": {
            "*HELP_CLOSURE_CODE": "Successful"
    }
}
```

The server stanza provides details on which server to connect to and which user and password to use. These must be provided by your local Extraview administrator.

The create stanza allows you set default fields when creating a new ticket. The close stanza does the same for when closing tickets. 

Note that any field that starts with a '*' character is expected to be an Extraview enumeration that will be auto resolved. For unknown reasons, Extraview requires the connecting API to resolve out the magic numbers used in enumerations. Use ```ev_view -d ${EV ID}``` to see what are the possible fields that can be provided to the configuration.
