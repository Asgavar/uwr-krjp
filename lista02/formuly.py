# -*- coding: utf-8 -*-

import itertools
import wyjatki


class Formula:
    """
    Bazowa klasa, ktora rozszerzaja poszczegolne formuly. Kazda z podklas
    posiada:
    * metode oblicz(zmienne: dict), zwracajaca odpowiednio wartosc bool dla
    przekazanego przez argument wartosciowania
    * jesli klasa jest operatorem przyjmujacym dwa operandy: pola op1 oraz op2
    Ponadto, klasa Zmienna posiada pole var_name przechowujace jej nazwe (np 'p'),
    a Not - pole expr bedace jej jedynym operandem.
    """
    def uzyte_zmienne(self, zbior):
        """
        Rekurencyjnie schodzi w dol danej formuly, zliczajac uzyte
        wewnatrz niej zmienne.

        Zwraca:
            Set zawierajacy nazwy wszystkich uzytych w formule zmiennych.
        """
        if isinstance(self, Zmienna):
            # gdy formula sama jest zmienna, 'dopisuje sie' do zbioru
            zbior.add(self.var_name)
            return zbior
        if isinstance(self, Not):
            return self.expr.uzyte_zmienne(zbior)
        if isinstance(self, (Prawda, Falsz)):
            return zbior
        # '|' zadziala w tym wypadku jak suma zbiorow
        return self.op1.uzyte_zmienne(zbior) | self.op2.uzyte_zmienne(zbior)

    def czy_tautologia(self):
        """
        Dzialanie opiera sie na stworzeniu listy zlozonej z takiej liczby
        True i False, ile jest zmiennych w danej formule, a nastepnie sprawdzeniu
        wszystkich mozliwosci wartosciowan przez dobor kazdej mozliwej kombinacji
        indeksow w ww liscie dla kazdej ze zmiennych.

        Zwraca:
            True, jesli dla kazdego z mozliwych wartosciowan formula okazala sie spelniona.
            False w przeciwnym przypadku.
        """
        zmienne = set()
        zmienne = list(self.uzyte_zmienne(zmienne))
        liczba_zmiennych = len(zmienne)
        tf_pattern = [True * liczba_zmiennych, False * liczba_zmiennych]
        index_str = ''
        # do index_str wpisujemy wszystkie indeksy z tf_pattern
        for i in range(len(tf_pattern)):
            index_str += str(i)
        possibilities = itertools.permutations(index_str, liczba_zmiennych)
        # p to krotka zawierajaca tyle indeksow, ile jest zmiennych
        for p in possibilities:
            wartosci = {zmienne[i]: p[i] for i in range(liczba_zmiennych)}
            # jesli okazalo sie, ze istnieja wartosci dla ktorych formula jest falszywa
            if not self.oblicz(wartosci):
                return False
        # gdy wszystkie mozliwosci zostaly juz sprawdzone
        return True


class Prawda(Formula):
    def __str__(self):
        return 'true'

    def oblicz(self, zmienne):
        return True


class Falsz(Formula):
    def __str__(self):
        return 'false'

    def oblicz(self, zmienne):
        return False


class Zmienna(Formula):
    def __init__(self, var_name):
        self.var_name = var_name

    def __str__(self):
        return self.var_name

    def oblicz(self, zmienne):
        # jesli nie dostarczono wartosci dla tej zmiennej rzucany jest wyjatek
        if self.var_name not in zmienne:
            raise wyjatki.VariableValueNotProvidedException(self.var_name)
        return zmienne[self.var_name]


class Not(Formula):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f'(¬({self.expr}))'

    def oblicz(self, zmienne):
        return True if not self.expr.oblicz(zmienne) else False


class And(Formula):
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def __str__(self):
        return f'({self.op1} ∧ {self.op2})'

    def oblicz(self, zmienne):
        return self.op1.oblicz(zmienne) and self.op2.oblicz(zmienne)


class Or(Formula):
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def __str__(self):
        return f'({self.op1} ∨ {self.op2})'

    def oblicz(self, zmienne):
        return self.op1.oblicz(zmienne) or self.op2.oblicz(zmienne)


class Impl(Formula):
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def __str__(self):
        return f'({self.op1} ⇒ {self.op2})'

    def oblicz(self, zmienne):
        # implikacja jest falszywa jedynie wtedy, gdy Prawda implikuje Falsz
        return not (
            self.op1.oblicz(zmienne) and not self.op2.oblicz(zmienne)
        )


class Equiv(Formula):
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def __str__(self):
        return f'({self.op1} ⇔ {self.op2})'

    def oblicz(self, zmienne):
        return self.op1.oblicz(zmienne) == self.op2.oblicz(zmienne)
