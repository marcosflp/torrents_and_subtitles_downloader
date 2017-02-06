# -*- coding: utf-8 -*-

import os
import sys
import subscope
import time

from core.thepiratebayapi import ThePirateBayApi
from core.torrentclient import TorrentClient

class View(object):
    result_list = []

    def __init__(self):
        os.system('clear')
        self.client = TorrentClient()
        self.tpb = ThePirateBayApi()

        self.menu_options = {
            '1': self.search_general,
            '2': self.search_serie_season,
            '3': self.search_serie_episode,
            '4': self.status,
            '0': self.exit
        }

    def main(self):
        option = self.menu()

        try:
            self.result_list = self.menu_options[option]()
        except Exception as e:
            os.system('clear')
            print e.message
            print "INVALID OPTION!\n"
            return self.main()

        if option != 0 and option != 4 and self.result_list:
            self.print_results()
            self.menu_download()
            os.system('clear')
            self.client.status()

        return self.main()

    def menu(self):
        print "---------------------------"
        print "Choose an option to search"
        print "---------------------------"
        print "1 - Search Anything"
        print "2 - Search Serie by Season"
        print "3 - Search Serie by Episode"
        print "4 - Download Status"
        print "0 - Exit"

        return raw_input("\nOption: ")

    def menu_download(self):
        print "\nChoose an option"
        print "----------------"
        print "1 - Download One"
        print "2 - Download All"
        print "0 - Return"

        option_menu = raw_input("\nOption: ")

        if option_menu == '0':
            return None

        if option_menu == '1':
            option_download = int(raw_input("Which one to download: ")) - 1

            obj = self.result_list[option_download]
            obj['type'] = 'general'
            self.client.add_magnet(obj=obj)

            print "File added. Try call clinet.status() to check the progress"

        if option_menu == '2':
            season_list = []
            for obj in self.result_list:
                obj['type'] = 'season'
                season_list.append(obj)
                self.client.add_magnet(season_list=season_list)

            print "File added. Try call clinet.status() to check the progress"

        return None

    def search_general(self, clear=True):
        if clear:
            os.system('clear')

        name = raw_input("Search: ")
        return self.tpb.search(name)

    def search_serie_season(self, clear=True):
        if clear:
            os.system('clear')

        serie_name = raw_input("Series name: ")
        season = raw_input("Season: ")
        return self.tpb.search_season(serie_name, season)

    def search_serie_episode(self, clear=True):
        if clear:
            os.system('clear')

        serie_name = raw_input("SERIES NAME: ")
        season = raw_input("SEASON: ")
        episode = raw_input("EPISODE: ")
        return self.tpb.search_episode(serie_name, season, episode)

    def status(self):
        self.client.status()

    def exit(self, m=0):
        return sys.exit(m)

    def print_results(self):
        index = 1

        print "\nResults found:"
        for result in self.result_list:
            print "    [{}] - {} {}".format(index, result['title'], ''.join(map(str, result['size'])))
            index += 1
        return None

View().main()
