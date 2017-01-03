import libtorrent as lt
import time

ses = lt.session()
ses.listen_on(6881, 6891)

link = "magnet:?xt=urn:btih:7e919e4346ae224a89ac4b5330a7fba2d54118b6&dn=Westworld.S01E01.1080p.HDTV.6CH.x265.HEVC-PSA.mkv&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Fzer0day.ch%3A1337&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Fexodus.desync.com%3A6969"

params = { 'save_path': '.', \
        'storage_mode': lt.storage_mode_t.storage_mode_sparse }

h = lt.add_magnet_uri(ses, link, params)

s = h.status()
while (not s.is_seeding):
        s = h.status()

        state_str = ['queued', 'checking', 'downloading metadata', \
                'downloading', 'finished', 'seeding', 'allocating']

        print '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
                (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                s.num_peers, state_str[s.state])

        time.sleep(1)
