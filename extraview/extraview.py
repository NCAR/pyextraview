#!/usr/bin/python
import argparse
import requests
import xml.etree.ElementTree
import re
from nlog import vlog,die_now

class client:
    """ Extraview Client """

    user	= None
    password	= None
    url		= None
    fields_cache = {}
    """ Cache of Extraview fields """


    def __init__(self, user, password, url):
	self.user = user
	self.password = password
	self.url = url

    def http_get(self, params):
	""" Perform a get request against extraview
	    return request object
	    params: get parameters to hand to extraview
	"""
	_params = {
		'user_id': self.user,
		'password': self.password,
	    }
	_params.update(params)
	 
	return requests.get(self.url, params=_params)
    def http_get_xml(self, params):
	""" Perform a get request against extraview that will return XML format
	    return request object
	    params: get parameters to hand to extraview
	"""

	r = self.http_get(params)
	return xml.etree.ElementTree.fromstring(r.text)
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
	 for efield, evalue in fields.iteritems():
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
	    return None

	members = self.get_group_members(group)
	if members is None or user is None:
	    return None

	for member, name in members.iteritems():
	    if name.lower() == user.lower():
		return name;

	if allow_nonmember:
	    return user
	else:
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
	@param EVSETUP extraview setup array
	@return ev response or FALSE on error
	@see http://docs.extraview.com/site/extraview-64/application-programming-interface/insert 
	"""
	params = {
	    'statevar':	    'insert',
	    #'p_template_file' => 'file.html',
	    'username_display': 'ID',
	    'send_email':	    'no',
	    'AREA':		    1, #cisl
	    'PROJECT':	    1, #help desk 
	    'HELP_LOGIN':	    originator,
	    'REQUESTOR_NAME':   'auto',
	    'PRIORITY':	    'P3', #Regular
	    'REQUESTOR_EMAIL':  'donotreply@ucar.edu',
	    'HELP_TYPE':	    67, #CISL
	    'CONTACT_PHONE':    '303-497-2400',
	    'SUBMISSION_TYPE':  227, #Web
	    'SHORT_DESCR':	    title,
	    'DESCRIPTION':	    description
	    #'EMAIL_CUSTOMER' => 'user@example.com',
	    #'HELP_CUST_EMAIL_2' => 'user@example.com'
	}
	params.update(fields)

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

	if grpid is None:
	    return None

 	params = {
	    'STATUS':		    'TRANSFERRED',
	    'HELP_ASSIGN_GROUP':    grpid
	}              
	params.update(fields)

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
	params.update(fields)

	return self.http_get_xml(params)
 
    def get_priority(self, priority):
	""" Get EV priority field value from string priority"""
	return self.get_field_value_to_field_key('PRIORITY', priority)

    def close(self, id, comment, fields = {}):
	""" Close extraview ticket """
	params = {
	    'STATUS':			'CLOSED',
	    'HELP_CUSTOMER_COMMENTS':	comment,
	    'HELP_CLOSURE_CODE':	self.get_field_value_to_field_key('HELP_CLOSURE_CODE', 'Successful') 
	}
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
