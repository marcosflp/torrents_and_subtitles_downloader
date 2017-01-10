# -*- coding: utf-8 -*-

import libtorrent as lt
import time
from thepiratebayapi import ThePirateBayApi

serie_name = raw_input("Series name: ")
season = raw_input("Season: ")

tpb = ThePirateBayApi()
episodes = tpb.search_season(serie_name, season)


ses = lt.session()
ses.listen_on(6881, 6891)

params = { 'save_path': './downloads',
           'storage_mode': lt.storage_mode_t.storage_mode_sparse }

for episode in episodes:
    print "Adding {} {} {}".format(episode['title'], episode['size'][0], episode['size'][1].upper())
    h = lt.add_magnet_uri(ses, episode['link'], params)

state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']
s = h.status()
first_minutes = 10
while not s.is_seeding:
        s = h.status()
        print '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers, state_str[s.state])

        if not first_minutes <= 0:
            time.sleep(1)
            first_minutes -= 1
        else:
            time.sleep(60)
