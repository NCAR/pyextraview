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
import unittest
import logging as log
from xml.etree import ElementTree
from .context import extraview

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.LongMessage = True
        log.basicConfig(level=log.DEBUG)

    def runTest(self):
        EV = extraview.connect()
        assert EV
        config = EV.config
        assert config
        ct = config['test']
        ctc = ct['create']

        id = EV.create(
            ctc['originator'],
            ctc['group'],
            ctc['user'],
            ctc['title'],
            ctc['description']
        )
        assert id
        log.debug('created: %s' % (id))

        s = EV.get_issue(id)
        assert s
        #ElementTree.dump(s)

        assert EV.add_resolver_comment(id, ct['resolver comment'])
        assert EV.add_user_comment(id, ct['user comment'])
        assert EV.add_user_comment(id, ct['user comment'])
        cta = ct['assign']
        assert EV.assign_group(id, cta['group'], cta['user'])

        self.assertEqual(s.find('ID').text, id)

        assert EV.close(id, ct['close']['comment'])

if __name__ == '__main__':
    unittest.main()
