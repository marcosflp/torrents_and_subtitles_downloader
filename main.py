# -*- coding: utf-8 -*-

import libtorrent as lt
import time
import os
from thepiratebayapi import ThePirateBayApi
from tabulate import tabulate

def is_all_torrents_finished(handler_list):
    for i in handler_list:
        if not i.is_finished():
            return False

    return True

serie_name = raw_input("Series name: ")
season = raw_input("Season: ")

tpb = ThePirateBayApi()
episodes = tpb.search_season(serie_name, season)


ses = lt.session()
ses.listen_on(6881, 6891)

params = { 'save_path': './downloads',
           'storage_mode': lt.storage_mode_t.storage_mode_sparse }

handler = []
for episode in episodes:
    handler.append(lt.add_magnet_uri(ses, episode['link'], params))

state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating', '?']
first_minutes = 10*60

headers = ['Episode', 'Complete %', 'Download kb/s', 'Up Kb/s', 'Peers', 'State']

while not is_all_torrents_finished(handler):
    final_list = []

    for torrent in handler:
        status = torrent.status()

        if torrent.status().has_metadata:
            title = torrent.get_torrent_info().name()
        else:
            title = "-----"

        final_list.append([title,
                           status.progress * 100,
                           status.download_rate / 1000,
                           status.upload_rate / 1000,
                           status.num_peers,
                           state_str[status.state]])

    os.system("clear")
    print(tabulate(final_list, headers=headers, tablefmt='orgtbl'))

    # for i in handler:
    #     s = i.status()
    #     print '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers, state_str[s.state])

    time.sleep(1)
