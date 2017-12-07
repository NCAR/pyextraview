# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
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

        self.assertEqual(s.find('ID').text, id)

        EV.close(id, ct['close']['comment'])

        assert 0


if __name__ == '__main__':
    unittest.main()
