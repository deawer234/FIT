"""
Name: processXML.py
Main file: interpret.py
Caption:  Class process XML source
Author: Magdaléna Ondrušková <xondru16@stud.fit.vutbr.cz>
Date: 28.03.2020
"""
import xml.etree.ElementTree as ET
from intlib.instruction import InstructionChecker
from intlib.error import Error, ERRConstruction
import re
import sys
from intlib.frames import Frames
from intlib.run_code import Interpret
from operator import itemgetter


class XMLparser:
    def __init__(self, xml_source, input_source):
        self.xml_source = xml_source
        self.input_source = input_source
        self.code = []

    def parse(self, stats):
        try:
            my_tree = self.start_parsing()
            my_root = self.parse_header(my_tree)
            self.parse_program(my_root, stats)
        except ET.ParseError as msg:
            err = Error(31, msg)
            err.err_out()
        except ERRConstruction as msg:
            err = Error(32, msg)
            err.err_out()

    def start_parsing(self):
        if self.xml_source is None:
            self.xml_source = sys.stdin
        try:
            my_tree = ET.parse(self.xml_source)
        except FileNotFoundError:
            err = Error(11, "Cannot open input XML file.")
            err.err_out()
        return my_tree

    @staticmethod
    def parse_header(mytree):
        """
        Function control XML header that should be in form of: <program language="IPPcode20">
        """
        my_root = mytree.getroot()
        if my_root.tag != "program":
            raise ERRConstruction("Root element isn't 'program'.")
        for attrib, val in my_root.attrib.items():
            val = val.upper()
            if attrib == "language" and val != "IPPCODE20":
                raise ERRConstruction("Attribute language has to have value 'IPPcode20'.")
            elif attrib == "language" and val == "IPPCODE20":
                continue
            elif attrib != "name" and attrib != "description":
                raise ERRConstruction("Not allowed attribute: {} in root.".format(attrib))
        return my_root

    def parse_program(self, my_root, stats):
        """
        Function parse XML instruction code and controls instruction attribute (order and opcode)
        #TODO order can be in different structure (1 5 7 4 ) and this func should order it
        At the end, function calls code.control which basically interpret instructions
        """
        arg_re = re.compile("arg[0-9]+")  # regex for controlling arguments
        frame = Frames()
        code = Interpret(frame, self.input_source, stats)

        order_number = []
        for my_child in my_root:
            if my_child.tag != "instruction":
                raise ERRConstruction("{} should be instruction.".format(my_child.tag))
            if "opcode" not in my_child.attrib or "order" not in my_child.attrib:
                raise ERRConstruction("Missing opcode or order in instruction attribute.")

            opcode = ''
            actual_order = 0
            for attrib, val in my_child.attrib.items():
                if attrib == "order":
                    try:
                        if int(val) < 1:
                            raise ERRConstruction("Order lesser or equal 0.")
                    except ValueError:
                        raise ERRConstruction("Trying to convert string that doesn't contain number to int.")
                    if int(val) not in order_number:
                        order_number.append(int(val))
                        actual_order = int(val)
                    else:
                        raise ERRConstruction("Duplicit order!")
                elif attrib == "opcode":
                    opcode = val.upper()
                else:
                    raise ERRConstruction("Attribute isn't opcode or order!")
            self.parse_arguments(my_child, opcode, actual_order, arg_re, code)
        code.control()

    @staticmethod
    def parse_arguments(my_child, opcode, actual_order, arg_re, code,):
        """
        Function controls arguments of instruction
        #TODO check number of arguments and order it
        :param my_child: One instruction
        :param opcode: Opcode of instructon
        :param arg_re: Regex for instruction - already compiled
        :param code: List with all instruction (opcode + arguments)
        """
        interpret = InstructionChecker()
        arguments = []
        arg_list = []
        for my_arguments in my_child:
            if arg_re.fullmatch(my_arguments.tag) is None:
                raise ERRConstruction("Expected tag arg(number), not {}".format(my_arguments.tag))
            arg_num = int(my_arguments.tag[3:])
            for attribs, vals in my_arguments.attrib.items():
                if attribs != "type":
                    raise ERRConstruction("Unexpected attribute in arguments in instruction!")
            arg_list.append([arg_num, my_arguments.attrib["type"], my_arguments.text])
        arg_list.sort(key=itemgetter(0))
        i = 0
        while len(arg_list) > len(arguments):
            if arg_list[i][0] != i + 1:
                raise ERRConstruction("Missing arguments!")
            arguments.append([arg_list[i][1], arg_list[i][2]])
            i += 1
        interpret.check_instruction(opcode, arguments)
        code.code_to_interpret.append([actual_order, opcode, arguments])
