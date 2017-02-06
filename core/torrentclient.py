# -*- coding: utf-8 -*-

import libtorrent as lt
import os
import re
from tabulate import tabulate


class TorrentClient(object):

    def __init__(self):
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        self.torrents = []
        self.download_root_path = '../downloads/'

    def add_magnet(self, obj=None, season_list=None):
        """ Add a magnet torrent link (or list of links) to be downloaded. """

        params = { 'save_path': None,
                   'storage_mode': lt.storage_mode_t.storage_mode_sparse }

        if season_list:
            save_path = self.get_save_path(season_list[0]['title'])
            params['save_path'] = save_path

            for episode in season_list:
                t = lt.add_magnet_uri(self.session, episode['link'], params)
                self.torrents.append(t)
        elif obj:
            save_path = self.get_save_path(obj['title'])
            params['save_path'] = save_path

            t = lt.add_magnet_uri(self.session, obj['link'], params)
            self.torrents.append(t)
        else:
            # TODO: handle with call with no arguments
            pass

        return None

    def is_all_downloads_finished(self):
        for i in self.torrents:
            if not i.is_finished():
                return False

        return True

    def status(self):
        """ Print on terminal the status of all the torrents in the session """

        t_list = []
        headers = ['Episode', 'Complete %', 'Download kb/s', 'Up Kb/s', 'Peers', 'State']
        state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating', '?']

        for t in self.torrents:
            t_status = t.status()

            if t_status.has_metadata:
                t_title = t.get_torrent_info().name()
            else:
                t_title = "-----"

            t_list.append([t_title,
                           t_status.progress * 100,
                           t_status.download_rate / 1000,
                           t_status.upload_rate / 1000,
                           t_status.num_peers,
                           state_str[t_status.state]])

        os.system("clear")
        print(tabulate(t_list, headers=headers, tablefmt='orgtbl'))

        return None

    def get_save_path(self, title):
        # 1. Verificar se já existe uma pasta com nome do cine atravéz do atributo download_root_path
        #    e armazenar o path do cine em uma variavel, caso não exista a variavel tem valor vazio ex: ''
        # 2. Caso não exista pasta para o cine gerar uma nova a partir do título

        word_list = []
        if len(title.split(' ')) > 2:
            word_list = title.split(' ')
        elif len(title.split('.')) > 2:
            word_list = title.split('.')
        else:
            # TODO: configure an alert email function
            pass

        is_serie = lambda _title: True if re.search(r'S[0-9]{2}E[0-9]{2}', _title, re.I) else False

        # Generate path_name
        name_list = []
        if is_serie(title):
            for word in word_list:
                if re.search(r'S[0-9]{2}E[0-9]{2}', word, re.I):
                    name_list.append(word)
                    break
                else:
                    name_list.append(word)
        else:
            name_list = word_list

        path_name = '.'.join(map(lambda _word: str(_word).lower(), name_list))

        return path_name

def order_season_download_files_in_one_folder():
    pass

def plex_scheme():
    pass
