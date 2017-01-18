# -*- coding: utf-8 -*-

import requests
import time
import re
import sys
from lxml import html


class ThePirateBayApi(object):
    the_pirate_bay_search_link = "https://thepiratebay.org/search/"
    all_torrents_list = None
    url_request = None
    response = None

    paginator_index = '0'
    order_by = {'seeders': '99'}
    category = {'video': '200'}

    def search_season(self, serie_name, season):
        """
        :param serie_name: String Name of the serie to be searched
        :param season: Int of the serie season
        :return: list of episodes that complete the season
        """

        episodes_from_season = []
        episode = 1
        attempts = 2

        while episode <= 30:
            search_pharase = "{} S{:02d}E{:02d}".format(serie_name, int(season), episode)
            query = "{0}/{1}/{2}/{3}/".format(search_pharase, self.paginator_index, self.order_by['seeders'], self.category['video'])

            url = self.the_pirate_bay_search_link + query
            response = self._get(url)

            top_results = self._get_top10_torrents(response)
            if not top_results:
                attempts -= 1
                episode += 1
                if attempts >= 0:
                    continue
                else:
                    break

            print "Found: " + top_results[0]['title']
            episodes_from_season.append(top_results[0])
            episode += 1

        return episodes_from_season

    def search_episode(self, serie_name, season, episode):
        """
        :param serie_name: String Name of the serie to be searched
        :param season: Int of the serie season
        :param episode: Int of the serie episode
        :return: list of top 10 magnet linksof the serie episode
        """

        search_pharase = "{} S{:02d}E{:02d}".format(serie_name, int(season), int(episode))
        query = "{0}/{1}/{2}/{3}/".format(search_pharase, self.paginator_index, self.order_by['seeders'], self.category['video'])

        url = self.the_pirate_bay_search_link + query
        response = self._get(url)

        return self._get_top10_torrents(response)[:10]

    def search(self, search_pharase):
        """
        :param search_pharase: string that is used on search
        :return: list of top 10 magnet links
        """

        query = "{0}/{1}/{2}/{3}/".format(search_pharase, self.paginator_index, self.order_by['seeders'], self.category['video'])

        url = self.the_pirate_bay_search_link + query
        response = self._get(url)

        return self._get_top10_torrents(response)[:10]

    def _get(self, url):
        try:
            response = requests.get(url)
        except Exception:
            # Retry once, it could be a momentary overloaded server?
            time.sleep(3)
            try:
                response = requests.get(url)
            except Exception:
                print("Connection error!\nUnable to reach opensubtitles.org servers!", OSError)
                raise

        if response.status_code != 200:
            print("Connection error!\nResponse Status: {}".format(response.status_code))
            sys.exit(1)

        self.response = response
        self.url_request = response.url
        return response

    def _get_top10_torrents(self, response):
        """
        Returns a list of the top 10 links based on seeders
        :param response: response of a request
        :return: list
        """
        tree = html.fromstring(response.content)
        torrents_list = []
        cont = 1

        # Result not found
        if len(tree.xpath('//table[@id="searchResult"]/tr')) == 0:
            return torrents_list

        torrents_tree_list = tree.xpath('//table[@id="searchResult"]/tr')
        for item_tree in torrents_tree_list:
            data_tree = {
                'title': item_tree.xpath('.//td/div[@class="detName"]/a/text()'),
                'size': item_tree.xpath('./td[2]/font/text()'),
                'link': item_tree.xpath('./td[2]/a[1]/@href'),
                'seeds': item_tree.xpath('./td[3]/text()'),
                'leeches': item_tree.xpath('./td[3]/text()')
            }

            ## normalise data and validations
            data = { 'position': cont }

            title = data_tree['title']
            if title:
                if isinstance(title[0], basestring):
                    data['title'] = data_tree['title'][0]

            text = data_tree['size']
            if text:
                if isinstance(text[0], basestring):
                    text = text[0].encode('ascii', 'ignore').decode('ascii').strip()
                    re_size = re.search(r'size ([\d\.]+)\s?(\w+)', text, re.I)
                    if re_size:
                        data['size'] = (float(re_size.group(1)), re_size.group(2).lower())

            link = data_tree['link']
            if link:
                data['link'] = data_tree['link'][0]

            seeds = data_tree['seeds']
            if seeds:
                if isinstance(seeds, basestring):
                    data['seeds'] = int(seeds[0])

            leeches = data_tree['leeches']
            if leeches:
                if isinstance(leeches, basestring):
                    data['leeches'] = int(leeches[0])

            torrents_list.append(data)
            cont += 1

        self.all_torrents_list = torrents_list
        return torrents_list[:10]
