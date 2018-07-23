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
import sys
import syslog
import os

def vlog(level, string):
    vlevel = 3
    if 'VERBOSE' in os.environ:
        vlevel = int(os.environ['VERBOSE'])

    if vlevel >= level:
        print(string)

    syslog.syslog(string.encode('utf-8'))

def elog(string):
    sys.stderr.write('%s\n' % (string))

def die_now(string):
    """ Print error and die right now """
    elog(string)
    sys.exit(1)
 
def to_hex(string):
    """ Dumps string as hex """

    try:
        if len(string) > 0 and isinstance(string, str):
            #https://stackoverflow.com/questions/12214801/print-a-string-as-hex-bytes
            return ':'.join(x.encode('hex') for x in string)
    except Exception as err:
        vlog(1, 'Unable to convert string to hex')

    return None

def is_ascii(string):
    """ Determine is string only contains ascii characters """
    #https://stackoverflow.com/questions/196345/how-to-check-if-a-string-in-python-is-in-ascii
    return all(ord(c) < 128 for c in string)

