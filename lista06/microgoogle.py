#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import argparse
import re
import threading
import urllib.request
import html.parser
import multiprocessing as mp


class MicroGoogleHTMLParser(html.parser.HTMLParser):
    """
    Wyluskuje linki ze strony. Sa one dostepne pod atrybutem self.links.
    Dla prostoty implementacji i szybkosci dzialania, za linki uznawane sa URLe
    w pelnej formie (np http://www.example.com), nie uzywajace SSL.
    """
    def __init__(self):
        super().__init__()
        self.links = []

    def _is_url_valid(self, url):
        return 'https' not in url and url.startswith('http')

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (atr, val) in attrs:
                if atr == 'href':
                    if self._is_url_valid(val):
                        self.links.append(val)


class MicroGoogle:
    """
    Wystawia interfejs przypominajacy Pythonowy slownik.
    """
    def __init__(self, startpage, depth):
        self.startpage = startpage
        self.depth = depth
        self.links = []
        self.links.append(startpage)
        page = urllib.request.urlopen(startpage)
        # 'superwatek', nie zakonczy sie poki nie zakoncza sie watki wywolane
        # przez niego
        getting_links = threading.Thread(target=self._get_links, args=(page, 1))
        getting_links.start()
        getting_links.join()
        for x in self.links:
            print(x)

    def __getitem__(self, key):
        """
        Zwraca liste krotek skladajacych sie z adresu strony i liczby wystapien
        szukanego slowa.
        """
        self._set_keyword(key)
        with mp.Pool() as pool:
            ret = pool.map(self._search, self.links)
        ret = list(filter(lambda x: x[1] != 0, ret))
        ret = sorted(ret, key=lambda x: x[1], reverse=True)
        return ret

    def _get_links(self, page, rec_depth):
        """
        Rekurencyjnie wpisuje wszystkie napotkane odnosniki do self.links,
        zaglebiajac sie przy tym nie glebiej niz self.depth.
        """
        html_parser = MicroGoogleHTMLParser()
        html_parser.feed(str(page.read()))
        for link in html_parser.links:
            if link not in self.links:
                self.links.append(link)
                if rec_depth < self.depth:
                    next_page = urllib.request.urlopen(link)
                    threading.Thread(
                        target=self._get_links,
                        args=(next_page, rec_depth + 1)
                    ).start()

    def _search(self, url):
        """
        Zwraca liczbe wystapien keyword na stronie pod adresem url.
        """
        print(f'Sprawdzanie {url}')
        try:
            with urllib.request.urlopen(url, timeout=10) as page:
                return(url, len(re.findall(self.keyword, str(page.read()))))
        except Exception as e:
            print(f'Pomijanie strony: {url} z powodu: {e}')
            return (url, 0)

    def _set_keyword(self, keyword):
        self.keyword = keyword


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--startpage', type=str, required=True,
                        help='Strona, od ktorej rozpocznie sie przeszukiwanie')
    parser.add_argument('-d', '--depth', type=int, required=True,
                        help='Glebokosc przeszukiwania')
    parser.add_argument('-k', '--keyword', type=str, required=True,
                        help='Szukane slowo kluczowe')
    args = parser.parse_args()
    mg = MicroGoogle(args.startpage, args.depth)
    print(mg[args.keyword])
