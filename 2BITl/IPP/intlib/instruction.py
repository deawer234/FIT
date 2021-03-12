"""
Name: instruction.py
Main program: interpret.py
Caption:  Class process instructions (opcode + arguments)
Author: Magdaléna Ondrušková <xondru16@stud.fit.vutbr.cz>
Date: 27.03.2020
"""

import re
from intlib.error import ERRConstruction
from intlib.frames import Frames


class InstructionChecker:
    def __init__(self):
        self.label_name_re = re.compile("[A-Za-z0-9$&%*_!?\-]*")
        self.var_name_re = re.compile("(GF|LF|TF)@[A-Za-z_\-$&%*!?]+[0-9A-Za-z_\-$&%*!?]*")
        self.const_name_re = re.compile("(int@[+\-]?[0-9]*|bool@(true|false)|nil@nil)")
        self.opcode = ["CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK"]
        self.opcode_var = ["DEFVAR", "POPS"]
        self.opcode_var_symb1_symb2 = ["ADD", "SUB", "MUL", "IDIV", "DIV", "LT", "GT", "EQ", "AND", "OR",
                                       "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR"]
        self.opcode_var_symb = ["NOT", "MOVE", "INT2CHAR", "STRLEN", "TYPE", "INT2FLOAT", "FLOAT2INT"]
        self.opcode_symb = ["PUSHS", "WRITE", "EXIT", "DPRINT"]
        self.opcode_label = ["LABEL", "JUMP", "CALL", "JUMPIFEQS", "JUMPIFNEQS"]
        self.opcode_label_symb1_symb2 = ["JUMPIFEQ", "JUMPIFNEQ"]
        self.opcode_var_type = ["READ"]
        self.opcode_stack = ["CLEARS", "ADDS", "SUBS", "MULS", "IDIVS", "DIVS", "LTS", "GTS", "EQS", "ANDS", "ORS",
                             "NOTS", "INT2CHARS", "STRI2INTS", "INT2FLOATS", "FLOAT2INTS"]
        self.frames = Frames()

    def check_instruction(self, opcode, args):
        """
        Function controls syntax and lexical side of instruction
        Function also rewrites symbol in args after checking (delete escape sequences)
        At the end, function adds opcode and it's arguments to list of all code that is later used in interpretation
        :param opcode: Name of instruction
        :param args: Arguments of instruction
        :param code: List where is all code stored
        """
        opcode = opcode.upper()  # changes given opcode to uppercase
        if opcode in self.opcode:
            self.control_number_of_arguments(expected_arguments=0, real_number_of_arguments=len(args))
        elif opcode in self.opcode_var:
            self.control_number_of_arguments(expected_arguments=1, real_number_of_arguments=len(args))
            self.control_var(var_type=args[0][0], var_name=args[0][1], var_name_re=self.var_name_re)
        elif opcode in self.opcode_var_symb1_symb2:
            self.control_number_of_arguments(expected_arguments=3, real_number_of_arguments=len(args))
            self.control_var(var_type=args[0][0], var_name=args[0][1], var_name_re=self.var_name_re)
            args[1][0], args[1][1] = self.control_symb(self, symb_type=args[1][0], symb_name=args[1][1],
                                                       var_name_re=self.var_name_re,
                                                       const_name_re=self.const_name_re)
            args[2][0], args[2][1] = self.control_symb(self, symb_type=args[2][0], symb_name=args[2][1],
                                                       var_name_re=self.var_name_re,
                                                       const_name_re=self.const_name_re)
        elif opcode in self.opcode_var_symb:
            self.control_number_of_arguments(expected_arguments=2, real_number_of_arguments=len(args))
            self.control_var(var_type=args[0][0], var_name=args[0][1], var_name_re=self.var_name_re)
            args[1][0], args[1][1] = self.control_symb(self, symb_type=args[1][0], symb_name=args[1][1],
                                                       var_name_re=self.var_name_re,
                                                       const_name_re=self.const_name_re)
        elif opcode in self.opcode_symb:
            self.control_number_of_arguments(expected_arguments=1, real_number_of_arguments=len(args))
            args[0][0], args[0][1] = self.control_symb(self, symb_type=args[0][0], symb_name=args[0][1],
                                                       var_name_re=self.var_name_re,
                                                       const_name_re=self.const_name_re)
        elif opcode in self.opcode_label:
            self.control_number_of_arguments(expected_arguments=1, real_number_of_arguments=len(args))
            self.control_label(label_type=args[0][0], label_name=args[0][1], label_name_re=self.label_name_re)
        elif opcode in self.opcode_label_symb1_symb2:
            self.control_number_of_arguments(expected_arguments=3, real_number_of_arguments=len(args))
            self.control_label(label_type=args[0][0], label_name=args[0][1], label_name_re=self.label_name_re)
            args[1][0], args[1][1] = self.control_symb(self, symb_type=args[1][0], symb_name=args[1][1],
                                                       var_name_re=self.var_name_re,
                                                       const_name_re=self.const_name_re)
            args[2][0], args[2][1] = self.control_symb(self, symb_type=args[2][0], symb_name=args[2][1],
                                                       var_name_re=self.var_name_re,
                                                       const_name_re=self.const_name_re)
        elif opcode in self.opcode_var_type:
            self.control_number_of_arguments(expected_arguments=2, real_number_of_arguments=len(args))
            self.control_var(var_type=args[0][0], var_name=args[0][1], var_name_re=self.var_name_re)
            self.control_type(type_type=args[1][0], type_name=args[1][1])
        elif opcode in self.opcode_stack:
            self.control_number_of_arguments(expected_arguments=0, real_number_of_arguments=len(args))
        else:
            raise ERRConstruction("Instruction: {} doesnt exist in IPPcode20.".format(opcode))


    @staticmethod
    def control_number_of_arguments(expected_arguments, real_number_of_arguments):
        """
        Function check if the number of arguments is the same as expected
        :param expected_arguments: Number of expected arguments
        :param real_number_of_arguments:  Number of real arguments
        """
        if expected_arguments != real_number_of_arguments:
            raise ERRConstruction("Instruction has wrong number of arguments.")

    @staticmethod
    def control_var(var_type, var_name, var_name_re):
        """
        Function check shape of variable
        var[0] should be "var"
        var[1] is name of variable in shape Frame@{not-digit}{any char}
        :param var_type: Type of variable to be checked
        :param var_name: Name of variable to be checked
        :param var_name_re: pre-compiled regex for name of variable
        """
        if var_type != "var":
            raise ERRConstruction("Wrong XML argument type - expected variable, not {}.".format(var_type))
        if var_name_re.fullmatch(var_name) is None:
            raise ERRConstruction("Variable {} has wrong format. ".format(var_name))

    @staticmethod
    def control_symb(self, symb_type, symb_name, var_name_re, const_name_re):
        """
        Function checks shape of symbol - constant or var and
        If there is string constant, function transform escape sequences to chars and continues control
        :param symb_type: symbol type to be checked
        :param symb_name: symbol name to be checked
        :param var_name_re: variable regex
        :param const_name_re: constant regex
        :return Return symbol_type and symbol_name
        """
        if symb_type == "var":
            if var_name_re.fullmatch(symb_name) is None:
                raise ERRConstruction("Symbol should be variable, but name {} doesnt match.".format(symb_name))
        elif symb_type == "int" or symb_type == "bool" or symb_type == "nil":
            if symb_name is None:
                symbol = symb_type + "@"
            else:
                symbol = symb_type + "@" + symb_name
            if const_name_re.fullmatch(symbol) is None:
                raise ERRConstruction("{}: Wrong format of constant.".format(symbol))
        elif symb_type == "float":
            try:
                symb_name = float.fromhex(symb_name)
            except (ValueError, TypeError):
                raise ERRConstruction("Wrong format of float")
        elif symb_type == "string":
            if symb_name is None:
                symb_name = ''
            if re.search('[\s#]', symb_name) is not None:
                raise ERRConstruction("Symbol {} contains not allowed characters (white spaces, #).".format(symb_name))
            symb_name = self.escape_seq(symb_name)
            if re.search('[\\\\]', symb_name) is not None:
                raise ERRConstruction(
                    "Symbol {} contains not allowed characters (backspace not in escape seq)".format(symb_name))
        else:
            raise ERRConstruction("Symbol {} isnt constant nor variable.".format(symb_name))
        return symb_type, symb_name

    @staticmethod
    def escape_seq(symb_name):
        """
        Function transfers escape sequences to chars
        :param symb_name: Symbol_name to be transfered
        :return: symb_name - symb_name without escape sequences
        """
        escape_sequence = re.findall('(\\\\[0-9]{3})', str(symb_name))
        escape_set = set(escape_sequence)
        escape_unique = (list(escape_set))
        for x in escape_unique:
            symb_name = symb_name.replace(x, chr(int(x[1:])))
        return symb_name

    @staticmethod
    def control_label(label_type, label_name, label_name_re):
        """
        Function checks shape of label
        :param label_type: label type to check
        :param label_name: label name to check by regex
        :param label_name_re: label regex
        """
        if label_type == "label":
            if label_name_re.fullmatch(label_name) is None:
                raise ERRConstruction("Label {} doesnt have right name.".format(label_name))
            else:
                return
        else:
            raise ERRConstruction("{} should be label, it isnt.".format(label_name))

    @staticmethod
    def control_type(type_type, type_name):
        """
        Function check syntax of type
        :param type_type: Must be type in argument
        :param type_name: Must be in types  else it's error
        """
        types = ["bool", "int", "string", "nil", "float"]
        if type_type == "type":
            if type_name not in types:
                raise ERRConstruction("{} : Wrong format of type.".format(type_name))
        else:
            raise ERRConstruction("Expected type, got {}".format(type_name))
