# -*- coding: utf-8 -*-


class VariableValueNotProvidedException(Exception):
    def __init__(self, var_name):
        self.var_name = var_name

    def __str__(self):
        return f'Nie dostarczono wartosci zmiennej {self.var_name}'
