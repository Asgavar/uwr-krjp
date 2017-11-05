#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
Algorytm uzyty tu do sprawdzania pierwszosci jest oczywiscie ekstremalnie
niewydajny, ale dzieki temu latwiej bedzie porownac implementacje miedzy soba.
"""

import sys
import timeit


def primes_comprehension(n):
    """
    Wszystkie x, ktore nie maja 0 w liscie reszt z dzielen przez
    n = 2, 3..(x-1)
    """
    return [x for x in range(2, n) if 0 not in [x % y for y in range(2, x)]]


def primes_functional(n):
    """
    Odfiltrowanie takich x, ktore nie maja 0 w liscie reszt ^...
    """
    return filter(lambda x: 0 not in map(lambda y: x % y, range(2, x)), range(2, n))  # noqa: E501


class PrimesIter:
    def __init__(self, up_to):
        """
        Argumentem up_to ustawiamy gorny zakres iteracji (jak np w range(n)).
        """
        self.current = 2
        self.up_to = up_to

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self.current > self.up_to:
                raise StopIteration
            is_prime = True
            for x in range(2, self.current):
                if self.current % x == 0:
                    is_prime = False
                    self.current += 1
                    break
            if is_prime:
                ret = self.current
                self.current += 1
                return ret


if __name__ == '__main__':
    # w tym przypadku implementacja ArgParsera bylaby chyba
    # przerostem formy nad trescia
    if len(sys.argv) != 2:
        print('Nalezy podac najwieksze n przez wiersz polecen')
        exit()
    max_arg = int(sys.argv[1])  # najwyzsza potega 10, ktora sprawdzamy
    # wyniki pomiarow dla kazdej z funkcji
    comp_times = []
    func_times = []
    iter_times = []
    timeit_setup = '''from l04z01 import (
        primes_comprehension,
        primes_functional,
        PrimesIter
    )'''
    args = [10 ** x for x in range(max_arg)]
    for arg in args:
        c = timeit.timeit(
                f'primes_comprehension({arg})',
                setup=timeit_setup, number=1)
        f = timeit.timeit(
                f'list(primes_functional({arg}))',
                setup=timeit_setup, number=1)
        i = timeit.timeit(
                f'list(PrimesIter({arg}))',
                setup=timeit_setup, number=1)
        comp_times.append(round(c, 4))
        func_times.append(round(f, 4))
        iter_times.append(round(i, 4))
    # wydruk do wiersza polecen
    arg_rjust = len(str(10 ** max_arg))
    comp_times = list(map(lambda x: str(x), comp_times))
    func_times = list(map(lambda x: str(x), func_times))
    iter_times = list(map(lambda x: str(x), iter_times))
    print(f'{"".rjust(arg_rjust)} | skladana | funkcyjna | iterator')
    for i in range(len(comp_times)):
        print(f'{str(args[i]).rjust(arg_rjust)} | {comp_times[i].rjust(len("skladana"))} | {func_times[i].rjust(len("funkcyjna"))} | {iter_times[i].rjust(len("iterator"))}')
