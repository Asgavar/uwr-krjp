#!/usr/bin/env bash

python -m timeit 'from lista03 import primes_comprehension; for p in primes_comprehension(100):print(p)'
python -m timeit 'from lista03 import primes_functional; primes_functional(100)'
python -m timeit 'from lista03 import perfects_comprehension; perfects_comprehension(100)'
python -m timeit 'from lista03 import perfects_functional; perfects_functional(100)'
