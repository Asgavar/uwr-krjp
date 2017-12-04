#!/usr/bin/env python3.6

import os
import sys
import time
from lista03 import *

if __name__ == '__main__':
    #sys.stdout = open(os.devnull, 'w')
    t0 = time.time()
    for p in primes_comprehension(10_000):
        print(p)
    prim_comp = time.time() - t0
    #
    t0 = time.time()
    for p in primes_functional(10_000):
        print(p)
    prim_func = time.time() - t0
    #
    t0 = time.time()
    for p in perfects_comprehension(10_000):
        print(p)
    perf_comp = time.time() - t0
    #
    t0 = time.time()
    for p in perfects_functional(10_000):
        print(p)
    perf_func = time.time() - t0
    #
    print(f'primes_comprehension(10_000): {prim_comp}s')
    print(f'primes_functional(10_000): {prim_func}s')
    print(f'perfects_comprehension(10_000): {perf_comp}s')
    print(f'perfects_functional(10_000): {perf_func}s')
