#!/usr/bin/env python3.6

"""
Pomocniczy skrypt parsujący i wyświetlający log profilera.
"""
import pstats

if __name__ == '__main__':
    p = pstats.Stats('output_profilowania.pstats')
    # według łącznego czasu wykonywania
    p.strip_dirs().sort_stats('cumulative').print_stats()
