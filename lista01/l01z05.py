#!/usr/bin/env python3

def tabliczka(x1, x2, y1, y2):
    kolumny = [i for i in range(x1, x2+1)]
    rzedy   = [i for i in range(y1, y2+1)]
    for kolumna in kolumny:
        # "" na poczatku aby zaczac od wciecia
        print("", kolumna, end="")
    print()
    for rzad in rzedy:
        iloczyny = [rzad * kolumna for kolumna in kolumny]
        # zmapowanie do str, poniewaz join nie przyjmuje int
        iloczyny = map(str, iloczyny)
        wypis = str(rzad) + " " + " ".join(iloczyny)
        print(wypis)

tabliczka(3, 5, 2, 4)
print("\n" * 5)
tabliczka(1, 10, 1, 10)
