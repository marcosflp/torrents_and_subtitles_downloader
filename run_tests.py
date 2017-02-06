import unittest
from tests.core.torrentclient_tests import TorrentClientTest


def suite():
    tests = ['test_get_save_path']

    return unittest.TestSuite(map(TorrentClientTest, tests))

clientTestSuite = suite()

unittest.TextTestRunner(clientTestSuite)

if __name__ == '__main__':
    unittest.main()
