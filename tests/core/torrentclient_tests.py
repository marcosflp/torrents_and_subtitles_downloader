import unittest
from core.torrentclient import *


class TorrentClientTest(unittest.TestCase):
    def setUp(self):
        self.torrent_client_cls = TorrentClient()

    def test_get_save_path(self):
        title1 = 'Westworld.S01E01.HDTV.x264-FUM[ettv]'
        self.assertEqual(self.torrent_client_cls.get_save_path(title1), 'westworld.s01e01')

        title2 = 'The Lord of the Rings: The Return of the King EXTENDED (2003) 10'
        self.assertEqual(self.torrent_client_cls.get_save_path(title2), 'the.lord.of.the.rings:.the.return.of.the.king.extended.(2003).10')

if __name__ == '__main__':
    unittest.main()
