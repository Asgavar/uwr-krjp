#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

def primes_comprehension(n):
    """
    Wszystkie x, ktore nie maja 0 w liscie reszt z dzielen przez n = 2, 3..(x-1)
    """
    return [x for x in range(2, n) if not 0 in [x % y for y in range(2, x)]]

def primes_functional(n):
    """
    Odfiltrowanie takich x, ktore nie maja 0 w liscie reszt ^...
    """
    return filter(lambda x: not 0 in map(lambda y: x % y, range(2,x)), range(2,n))
    #return filter(lambda x: not 0 in [x % y for y in range(2, x)], range(2, n))

def perfects_comprehension(n):
    """
    Wszystkie x, dla ktorych 1 + <dzielniki x mniejsze od n> jest rowne x
    """
    return [x for x in range(2, n) if x == sum([y for y in range(1, x) if x % y == 0])]

def perfects_functional(n):
    """
    Odfiltrowanie x, ktorych suma odfiltrowanych dzielnikow jest rowna x
    """
    return filter(lambda x: x == sum(filter(lambda y: x % y == 0, range(1, x))), range(2, n))

if __name__ == '__main__':
    print('Liczby pierwsze:')
    print(primes_comprehension(100))
    for p in primes_functional(100):
        print(p, end=' ')
    print('\n\nLiczby doskonale:')
    print(perfects_comprehension(100))
    for p in perfects_functional(100):
        print(p, end=' ')
