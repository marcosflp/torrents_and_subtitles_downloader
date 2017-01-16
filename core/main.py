# -*- coding: utf-8 -*-

import time
import os
import sys
import subscope
from thepiratebayapi import ThePirateBayApi
from core import TorrentClient


class View(object):
    chosen_option = None
    result = None
    tpb = None

    def __init__(self):
        self.tpb = ThePirateBayApi()

    def main(self):
        choices = {
            '1': self.search_general,
            '2': self.search_serie_season,
            '3': self.search_serie_episode,
            '0': self.exit
        }

        option = self.menu()

        try:
            self.result = choices[option]()
        except Exception:
            os.system('clear')
            print "INVALID OPTION!\n"

            return self.main()

        return self.result

    def menu(self):
        print "Choose an option to search"
        print "1 - Search Anything"
        print "2 - Search Serie by Season"
        print "3 - Search Serie by Episode"
        print "0 - Exit"

        return raw_input("\nOption: ")

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

        serie_name = raw_input("Series name: ")
        season = raw_input("Season: ")
        episode = raw_input("Episode: ")
        return self.tpb.search_episode(serie_name, season, episode)

    def exit(self, m=0):
        return sys.exit(m)
