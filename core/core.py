import libtorrent as lt
import os
import re
from tabulate import tabulate


class TorrentClient(object):
    torrents = []
    download_root_path = '../downloads/'
    download_season_path = ''

    def __init__(self):
        self.session = lt.session()
        self.session.listen_on(6881, 6891)

    def add_magnet(self, obj, season_list=None):
        """
        :param obj: {}
        :param season_list:
        :return:
        """
        if season_list:
            save_path = self.get_save_path(season_list[0])

            params = { 'save_path': save_path,
                       'storage_mode': lt.storage_mode_t.storage_mode_sparse }

            for episode in season_list:
                t = lt.add_magnet_uri(self.session, episode['link'], params)
                self.torrents.append(t)

        t = lt.add_magnet_uri(self.session, obj['link'], params)
        self.torrents.append(t)

        return None

    def is_all_finished(self):
        for i in self.torrents:
            if not i.is_finished():
                return False

        return True

    def status(self):
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

    def get_save_path(self, obj):
        name_splited = []

        if obj['search_choice'] == 'season' and self.download_season_path:
            if obj['title'].split('') > 2:
                name_splited = obj['title'].split('')
            elif obj['title'].split('.') > 2:
                name_splited = obj['title'].split('.')

        name = []
        for word in name_splited:
            match_obj = re.match(r'S[0-9]{2}E[0-9]{2}', word, re.I)
            if match_obj:
                name.append(word)
                break
            name.append(word)

        return '.'.split(map(str, name))

def order_season_download_files_in_one_folder():
    pass

def plex_scheme():
    pass
