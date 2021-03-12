"""
Name: variables.py
Main file: interpret.py
Caption:  Handles the variables of IPPcode20
Author: Magdaléna Ondrušková <xondru16@stud.fit.vutbr.cz>
Date: 29.03.2020
"""

from intlib.error import *

TYPE_INT = 0
TYPE_STRING = 1
TYPE_BOOL = 2
TYPE_NIL = 3
TYPE_FLOAT = 4


class Variable:
    def __init__(self, name):
        self.name = name
        self.type = None
        self.val = None

    def is_string(self):
        """
        Controls if variable has any value and if it's type string
        Returns variable value as string
        """
        if self.type is None:
            raise ERRMissVal("Variable defined, but has no-value.")
        elif self.type != TYPE_STRING:
            raise ERROperandType("Expected type string, got different type.")
        return str(self.val)

    def is_int(self):
        """
        Controls if variable has any value and if it's type int
        Returns variable as int
        """
        if self.type is None:
            raise ERRMissVal("Variable defined, but has no-value.")
        elif self.type != TYPE_INT:
            raise ERROperandType("Expected type int, got different type.")
        return int(self.val)

    def is_float(self):
        """
        Controls if variable has any value and if it's type float
        Returns variable as float
        """
        if self.type is None:
            raise ERRMissVal("Variable defined, but has no-value.")
        elif self.type != TYPE_FLOAT:
            raise ERROperandType("Expected type float.")
        return float(self.val)

    def is_nil(self):
        """
        Controls if variable has any value and if it's type nil
        """
        if self.type is None:
            raise ERRMissVal("Variable defined, but has no-value.")
        elif self.type != TYPE_NIL:
            raise ERROperandType("Expected type nil, got different type.")

    def is_bool(self):
        """
        Controls if variable has any value and if it's type bool
        """
        if self.type is None:
            raise ERRMissVal("Variable defined, but has no-value.")
        elif self.type != TYPE_BOOL:
            raise ERROperandType("Expected type bool, got different type.")
