# -*- coding: utf-8 -*-

import requests
import time
import re
from lxml import html


class ThePirateBayApi(object):
    the_pirate_bay_search_link = "https://thepiratebay.org/search/"
    tree = None

    def get_all_searson(self, serie, season):
        search_phrase = "{} {}"
    def search(self, text):
        """
        :param text: string that is used on search
        :return: list of top 10 magnet links
        """

        paginator_page = '0'
        order_by = {'seeders': '99'}
        category = {'video': '200'}

        path = "{0}/{1}/{2}/{3}".format(text, paginator_page, order_by['seeders'], category['video'])

        url = self.the_pirate_bay_search_link + path

        try:
            response = requests.get(url)
        except Exception:
            # Retry once, it could be a momentary overloaded server?
            time.sleep(3)
            try:
                response = requests.get(url)
            except Exception:
                print("Connection error!\nUnable to reach opensubtitles.org servers!")
                raise

        if response.status_code != 200:
            print("Connection error!\nResponse Status: {}".format(response.status_code))
            raise

        if re.search(r'No hits.', response.content, re.I):
            print("No result found. Try adding an asterisk or change the search phrase.")
            return None

        if len(html.fromstring(response.content).xpath('//table[@id="searchResult"]/tr')) == 0:
            print("No result found. Try adding an asterisk or change the search phrase.")
            return None

        top_results = self._get_magnet_links(response.content)

        return top_results[:10]

    def _get_magnet_links(self, response_content):
        tree = html.fromstring(response_content)
        torrents_list = []
        cont = 1

        torrents_tree_list = tree.xpath('//table[@id="searchResult"]/tr')

        for item_tree in torrents_tree_list:
            data_tree = {
                'title': item_tree.xpath('.//td/div[@class="detName"]/a/text()'),
                'size': item_tree.xpath('./td[2]/font/text()'),
                'link': item_tree.xpath('./td[2]/a[1]/@href'),
                'seeds': item_tree.xpath('./td[3]/text()'),
                'leeches': item_tree.xpath('./td[3]/text()')
            }

            ## normalise data
            data = { 'position': cont }

            # title
            title = data_tree['title']
            if title:
                data['title'] = data_tree['title'][0]

            # size
            text = data_tree['size']
            if text:
                text = text[0].encode('ascii', 'ignore').decode('ascii').strip()
                re_size = re.search(r'size ([\d\.]+)\s?(\w+)', text, re.I)
                if re_size:
                    data['size'] = (float(re_size.group(1)), re_size.group(2).lower())

            # magnet link
            link = data_tree['link']
            if link:
                data['link'] = data_tree['link'][0]

            # seeds
            seeds = data_tree['seeds']
            if seeds:
                data['seeds'] = int(seeds[0])

            # leeches
            leeches = data_tree['leeches']
            if leeches:
                data['leeches'] = int(leeches[0])

            torrents_list.append(data)
            cont += 1

        self.torrents_list = torrents_list

        return torrents_list

pb = ThePirateBayApi()

top = pb.search('westworld s01e02')
import pdb; pdb.set_trace()
