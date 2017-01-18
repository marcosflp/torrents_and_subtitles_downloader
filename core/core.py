import libtorrent as lt
import os
from tabulate import tabulate


class TorrentClient(object):
    torrents = []
    download_root_path = './downloads/'

    def __init__(self):
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        self.params = { 'save_path': os.path.join(self.download_root_path,),
                        'storage_mode': lt.storage_mode_t.storage_mode_sparse }

    def add_magnet_torrent(self, link=None, t_list=None):
        if t_list:
            for t_link in t_list:
                t = lt.add_magnet_uri(self.session, t_link, self.params)
                self.torrents.append(t)

        elif link:
            t = lt.add_magnet_uri(self.session, link, self.params)

        return self.torrents.append(t)

    def is_all_torrents_finished(self):
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

def order_season_download_files_in_one_folder():
    pass

def plex_scheme():
    pass
