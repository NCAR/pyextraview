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
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import requests
try:
        import xml.etree.cElementTree as ET
except ImportError:
        import xml.etree.ElementTree as ET
import re
from log import vlog,die_now
from .file import read_file_first_line

class client:
    """ Extraview Client """
    config	 = None
    fields_cache = {}
    """ Cache of Extraview fields """

    def __init__(self, config):
        self.config = config
    
    def http_get(self, params):
        """ Perform a get request against extraview
            return request object
            params: get parameters to hand to extraview
        """
        _params = {
        	'user_id': self.config['server']['user'],
        	'password': self.config['server']['password'],
            }
        _params.update(params)
         
        result = requests.get(self.config['server']['url'], params=_params)
        vlog(4, 'extraview http get: %s -> %s' % (result.url, result.status_code))
        vlog(5, 'extraview http get result:  %s' % (result.text))
        return result

    def http_get_xml(self, params):
        """ Perform a get request against extraview that will return XML format
            return request object
            params: get parameters to hand to extraview
        """
    
        r = self.http_get(params)
        return ET.fromstring(r.text.encode('utf-8'))
        #xml.etree.ElementTree.dump(b)
    
    def split_results(self, result):
        """
        @brief Split extraview row column split result
        @param resp Extraview response
        Should look like the following:
        
          3:NETS Add Remove
          5:Asset Mgt.
          8:NETS Travel
        
        @return array of left of : => right of : or FALSE on error
        """
        if len(result) > 0:
            data = {}
            for line in result.splitlines():
                fields = line.split(':')
                if len(fields) > 2:
                    data[fields[0]] = fields[1]
            return data
        else:
            return None
    
    def get_field_allowed(self, field, parentfield = None, parentvalue = None):
        """
        @brief Get list of allowed values for a given Extraview Field
        @note this will cache fields with out parents as they appear not to change
        @param field field name to query
        @param parentfield field name of parent field or NULL
        @param parentvalue value of parent field or NULL
        @return array of id => value or FALSE on error
        """
    
        if parentfield is None and field in self.fields_cache:
            return self.fields_cache[field];
    
        params = {
            'statevar': 'allowed_list',
            'field': field
        }
    
        if not parentfield is None:
            params['parent'] = parentfield;
            params['parent_val'] = parentvalue;
    
        values = self.split_results(self.http_get(params).text)
    
        if parentfield is None:
            self.fields_cache[field] = values
    
        return values
    
    
    def get_field_value_to_field_key(self, field, value, parentfield = None, parentvalue = None):
         """
         @brief Get Extraview Field index (case insensitive)
         EV has alot of fields that are enums. takes the given field and 
         looks up the allowed values and their keys. compares those values
         to extrat the correct key.
         @param field field name to query
         @param parentfield field name of parent field or NULL
         @param value value to compare against possible field values
         @param parentvalue value of parent field or NULL  
         @param EVSETUP extraview setup array
         @return ev key for given field for value or FALSE on error
         """
    
         fields = self.get_field_allowed(field, parentfield, parentvalue)
         if not fields is None:
             for efield, evalue in fields.items():
                 if evalue.lower() == value.lower():
                     return efield
    
         return None
    
    
    def get_group_id(self, group):
        """ Get Extraview Group ID (case insensitive) """
        return self.get_field_value_to_field_key('HELP_ASSIGN_GROUP', group)
    
    def get_group_members(self, group):
        """ Get Groups Members from an Extraview group """
        id = self.get_group_id(group)
        if id is None: 
            return None
    
        return self.get_field_allowed('ASSIGNED_TO', 'HELP_ASSIGN_GROUP', id)
    
    def get_group_member(self, group, user, allow_nonmember = False):
        """ 
         * @brief Check if user is member of group and get EV name for user
         * @param group Name of the group (note in EV all names are capped)
         * @param user name of user (can be NULL to unassign user)
         * @param EVSETUP extraview setup array
         * @param allow_nonmember allow a non-member of group to be returned (EV group membership is not enforced)
         * @return user EV name or FALSE on error
        """
        id = self.get_group_id(group)
        if id is None: 
            vlog(1, 'Unable to resolve group id {}'.format(group))
            return None
    
        members = self.get_group_members(group)
        if members is None or user is None:
            vlog(1, 'Group {} has no members'.format(group))
            return None
    
        for member, name in members.items():
            if name.lower() == user.lower():
                return name;
    
        if allow_nonmember:
            return user
        else:
            vlog(1, 'User {} is not a member of group {}'.format(user, group))
            return None
    
    def create(self, originator, group, user, title, description, fields = {}):
        """
        @brief Create new Extraview Issue (aka ticket)
        @param group Name of the group (note in EV all names are capped) or NULL
        @param user name of user or NULL
        @param title Issue title
        @param description Issue description
        @param fields array of fields to set (can override defaults)
        @param error set if return is false with EV error
        @return ev response or FALSE on error
        @see http://docs.extraview.com/site/extraview-64/application-programming-interface/insert 
        """
        params = {
            'statevar':	    'insert',
            #'p_template_file' => 'file.html',
            'username_display': 'ID',
            'HELP_LOGIN':	    originator,
            'SHORT_DESCR':	    title,
            'DESCRIPTION':	    description
        }
        self.resolve_config_fields(params, self.config['create'])
        self.resolve_config_fields(params, fields)
    
        grpid = self.get_group_id(group);
        if not grpid is None:
            params['HELP_ASSIGN_GROUP'] = grpid;
            params['STATUS']	    = 'TRANSFERRED',
     
        user = self.get_group_member(group, user, True);
        if not user is None:
            params['ASSIGNED_TO'] = user; 
            params['STATUS']	    = 'ASSIGNED',
    
        resp = self.http_get(params).text
        #example response: ID #78512 added.
        m = re.search('^ID #([0-9]+) added.', resp)
        if m:
            return m.group(1)
        else:
            vlog(2, 'Unable to create extraview ticket: %s' % (resp))
            return None
    
    def update(self, id, fields):
        """
        @brief Update Extraview Issue
        @param id Extraview issue id
        @param fields array containing field_name => new value
         The field names can be retrieving using a get on an issue
        @return ev response or FALSE on error
        """
        params = {
            'statevar':	    'update',
            'id':	    id,
            'username_display': 'ID'
        }
        params.update(fields)
    
        return self.http_get(params)
    
    def assign_group(self, id, group, user = None, fields = {}):
        """
        @brief Assign/transfer a Given user/group to a EV Issue
        @param id EV issue id
        @param group Name of the group (note in EV all names are capped)
        @param user name of user (can be NULL to unassign user)
        @return ev response or FALSE on error
        """
        grpid = self.get_group_id(group);
    
        if user:
            user = self.get_group_member(group, user);
            if user is None:
                vlog(1, 'Unable to resolve {}/{} to user'.format(group, user))
                return None
    
        if grpid is None:
            return None
    
        params = {
            'STATUS':		    'TRANSFERRED',
            'HELP_ASSIGN_GROUP':    grpid
        }              
        self.resolve_config_fields(params, fields)
    
        if not user is None:
            params['ASSIGNED_TO']   = user
            params['STATUS']	    = 'ASSIGNED',
        else:
            params['ASSIGNED_TO']   = '' #default to no user assigned
    
        return self.update(id, params)
    
    def search(self, fields, max):
        """
        @brief Search for EV issues
        @param field array of fields to search with their values
        @param max max number of issues to return 
        """
        params = {
            'statevar':		'search',
            #'p_template_file' => 'file.html',
            'username_display':	'ID',
            'record_start':	'1',
            'record_count':	'1',
            'page_length':	max, 
        }              
        self.resolve_config_fields(params, fields)
    
        return self.http_get_xml(params)
    
    def get_priority(self, priority):
        """ Get EV priority field value from string priority"""
        return self.get_field_value_to_field_key('PRIORITY', priority)
    
    def resolve_config_fields(self, params, config_params):
        """ Auto resolve out config Param fields that are marked with a * at start of name """

        for key, value in config_params.items():
            if key[0] == '*':
                field = key[1:]
                params[key[1:]] = self.get_field_value_to_field_key(field, value) 
            else:
                params[key] = value

    def close(self, id, comment, fields = {}):
        """ Close extraview ticket """
        params = {
            'STATUS':			'CLOSED',
            'HELP_CUSTOMER_COMMENTS':	comment,
        }
        self.resolve_config_fields(params, self.config['close'])
        params.update(fields)
    
        return self.update(id, params)
    
    def add_resolver_comment(self, id, comment, fields = {}):
        """ add resolver (admin only) comment extraview ticket """
        params = {
            'COMMENTS':	comment,
        }
        params.update(fields)
    
        return self.update(id, params)

    def add_user_comment(self, id, comment, fields = {}):
        """ add comment to user in extraview ticket """
        params = {
            'HELP_CUSTOMER_COMMENTS':	comment,
        }
        params.update(fields)
    
        return self.update(id, params)

    def get_issue(self, id):
        """
        @brief Retrieve Extraview Issue
        @param id Extraview issue id
        @return XML array of issue or FALSE on error
        """
        params = {
            'statevar':	'get',
            'id':	id
        }              
    
        return self.http_get_xml(params)
 
