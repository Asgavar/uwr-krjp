#!/usr/bin/env python3.6


class WordsIn:
    """
    Implementacja zaklada, ze:
    a) strumien nie zmieni swojej zawartosci podczas jego odczytu
    b) 'urwany' wyraz konczy sie w swoim wierszu myslnikiem, a
    zaczyna w nastepnym bez niego
    """
    def __init__(self, istream):
        omitted = '\n\t.,:;'
        with open(istream, 'r') as inp:
            self.lines = inp.readlines()
        for i in range(len(self.lines)):
            # usuniecie znakow interpunkcyjnych i bialych
            fixed = ''.join(filter(lambda c: c not in omitted, self.lines[i]))
            self.lines[i] = fixed

    def __iter__(self):
        return self

    def __next__(self):
        if self.lines[0] == '':
            self.lines.pop(0)
        # gdy oproznilismy obie linie naraz (ostatni wyraz sie urwal)
        if len(self.lines) > 1 and self.lines[1] == '':
            self.lines.pop(1)
        if not self.lines:
            raise StopIteration
        cur_line = self.lines[0].split(' ')
        # jesli aktualny wyraz nie jest ostatni w danej linii, mozemy po prostu
        # go zwrocic, poniewaz nie moze byc urwany
        if len(cur_line) > 1 or '-' not in cur_line[0]:
            ret = cur_line[0]
            replacement = ' '.join(cur_line[1:])
            self.lines[0] = replacement
            return ret
        # jednak jesli jest urwany, laczymy obie czesci
        first_half = cur_line[0][:-1]  # pomijamy '-' na koncu
        next_line = self.lines[1].split(' ')
        second_half = next_line[0]
        ret = first_half + second_half
        self.lines[0] = ' '.join(cur_line[1:])
        self.lines[1] = ' '.join(next_line[1:])
        return ret


if __name__ == '__main__':
    # dlugosci slow to klucze, ilosci to wartosci
    length_stats = {}
    for w in WordsIn('lista_jako_test.txt'):
        print(w)
        w_len = len(w)
        occurences = length_stats[w_len] if w_len in length_stats else 0
        length_stats[w_len] = occurences + 1
    print(length_stats)
