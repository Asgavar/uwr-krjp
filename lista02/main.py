#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from formuly import *

if __name__ == '__main__':
    # celowe sprawdzenie dzialania wyjatku
    try:
        print(Impl(Zmienna("x"), Zmienna("x")).oblicz(zmienne={}))
    except Exception as e:
        print(e)
    print('\nTesty __str__:')
    # (x ⇒ (y ∧ true))
    print(Impl(Zmienna("x"), And(Zmienna("y"), Prawda())))
    # (¬(p))
    print(Not(Zmienna('p')))
    # (true ⇔ false)
    print(Equiv(Prawda(), Falsz()))
    print('\nTesty obliczania wartosci:')
    # 'nie p' jesli p = true: powinno zwrocic False
    print(Not(Zmienna('p')), 'dla p = True: ', end='')
    print(Not(Zmienna('p')).oblicz({'p': True}))
    # true i false nigdy nie sa rownowazne
    print(Equiv(Prawda(), Falsz()), ': ', end='')
    print(Equiv(Prawda(), Falsz()).oblicz(zmienne={}))
    # prawda nie moze implikowac falszu
    print(Impl(Prawda(), Falsz()), ': ', end='')
    print(Impl(Prawda(), Falsz()).oblicz(zmienne={}))
    print('\nTesty tautologicznosci:')
    # 'y' rownowazne z 'nie y' - sprzecznosc, wiec nie tautologia
    print(Equiv(Zmienna('y'), Not(Zmienna('y'))), ': ', end='')
    print((Equiv(Zmienna('y'), Not(Zmienna('y')))).czy_tautologia())
    # p zawsze jest rownowazne z samym soba
    print(Equiv(Zmienna('p'), Zmienna('p')), ': ', end='')
    print(Equiv(Zmienna('p'), Zmienna('p')).czy_tautologia())
