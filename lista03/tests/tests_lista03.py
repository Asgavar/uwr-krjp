#!/usr/bin/env python3.6

import os
import sys
import unittest

sys.path.append(os.path.abspath('../'))
import lista03  # noqa: E402


class TestListaTrzy(unittest.TestCase):
    def setUp(self):
        self.primes_comp = lista03.primes_comprehension(1000)
        self.primes_func = list(lista03.primes_functional(1000))
        self.perfects_comp = lista03.perfects_comprehension(1000)
        self.perfects_func = list(lista03.perfects_functional(1000))

    def testBothPrimesHaveTheSameOutput(self):
        self.assertEqual(self.primes_comp, self.primes_func)

    def testBothPerfectsHaveTheSameOutput(self):
        self.assertEqual(self.perfects_comp, self.perfects_func)

    def testOneIsNotAPrimeComprehension(self):
        self.assertNotIn(1, self.primes_comp)

    def testOneIsNotAPrimeFunctional(self):
        self.assertNotIn(1, self.primes_func)

    def TwoIsAPrimeComprehension(self):
        self.assertIn(2, self.primes_comp)

    def TwoIsAPrimeFunctional(self):
        self.assertIs(2, self.primes_func)

    def testNoCompositeInPrimeComprehension(self):
        for x in self.primes_comp:
            for y in range(2, x):
                self.assertNotEqual(x % y, 0)

    def testNoCompositeInPrimeFunctional(self):
        for x in list(self.primes_func):
            for y in range(2, x):
                self.assertNotEqual(x % y, 0)

    def testNoImperfectInPerfectsComprehension(self):
        for perfect in self.perfects_comp:
            divisors = [x for x in range(1, perfect) if perfect % x == 0]
            self.assertEqual(sum(divisors), perfect)

    def testNoImperfectInPerfectsFunctional(self):
        for perfect in self.perfects_func:
            divisors = [x for x in range(1, perfect) if perfect % x == 0]
            self.assertEqual(sum(divisors), perfect)


if __name__ == '__main__':
    unittest.main()
