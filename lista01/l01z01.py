#!/usr/bin/env python3.6

import sys
import random

def rzut_kostka():
    return random.randint(1, 6)

n_tur        = int(sys.argv[1])
zwyciestwa1  = 0
zwyciestwa2  = 0
nr_tury      = 1
zwyciezca    = 0

while not zwyciezca:
    print("\n")
    print(f"Tura numer {nr_tury}:")
    print("-" * 20)
    nr_tury += 1
    # pierwsze dwa elementy to rzuty gracza 1, drugie dwa - 2
    rzuty = [rzut_kostka() for i in range(4)]
    wynik1, wynik2 = rzuty[0] + rzuty[1], rzuty[2] + rzuty[3]
    print(f"Rzuty gracza 1: {rzuty[0]}, {rzuty[1]}\tSUMA: {wynik1}")
    print(f"Rzuty gracza 2: {rzuty[2]}, {rzuty[3]}\tSUMA: {wynik2}")
    if wynik1 > wynik2: zwyciestwa1 += 1
    if wynik2 > wynik1: zwyciestwa2 += 1
    print(f"Gracz 1: {zwyciestwa1} zwyciestw")
    print(f"Gracz 2: {zwyciestwa2} zwyciestw")
    if (nr_tury > n_tur):
        # jesli nikt nie wygral, gra toczy sie dalej
        if zwyciestwa1 > zwyciestwa2: zwyciezca = 1
        if zwyciestwa2 > zwyciestwa1: zwyciezca = 2

print("\n")
print(f"Gracz {zwyciezca} wygrywa")
