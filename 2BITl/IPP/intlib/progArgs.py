"""
Name: progArgs.py
Main program: interpret.py
Caption:  Class process program arguments
Author: Magdaléna Ondrušková <xondru16@stud.fit.vutbr.cz>
Date: 28.03.2020
"""

from intlib.error import Error
import argparse as arg
import sys


class ProgArgParse(arg.ArgumentParser):
    def add_arg(self):
        """
        Function adds vaid program arguments and controls arguments
        Main fuction that calls other supproting function for controling arguments
        :return: xml_source, input_source - sources for program
        """
        self.add_argument("--help", action='store_true')
        self.add_argument("--source")
        self.add_argument("--input")
        self.add_argument("--stats")
        self.add_argument("--insts", action='store_true')
        self.add_argument("--vars", action='store_true')
        arguments = self.parse_args()
        xml_source, input_source, stats = self.check_arguments(arguments)
        return xml_source, input_source, stats

    def check_arguments(self, args):
        """
        Function control program arguments:
            - HELP - must be alone, can't be combined with other arguments
            - SOURCE - XML source
            - INPUT - INPUT source - for instruction READ
                    Must be at least one from SOURCE / INPUT present
            - STATS - File for statistics
            - INSTS - number of instruction done while running code
            - VARS - number of initialized vars in all frames
                    Must be with INSTS and VARS present arguments STATS
            - stats[File_to_save_stats, number_of_insts, number_of_vars]
        :param args:
        :return: sources of XML and INPUT - if one is not present, it is added as None
        """
        if args.help:
            if len(sys.argv) != 2:
                error = Error(10, "Other arguments with argument --help.")
                error.err_out()
            else:
                print("Program interpret.py interprets language IPPcode20.")
                print("Program loads source code in XML and writes output to STDOUT.")
                print("At least one argument --source or --input needs to be used, ")
                print("when none is used, the program ends with error.")
                print("If one is used, the other one is taken from STDIN.")
                exit(0)

        if not args.source and not args.input:
            error = Error(10, "At least one argument (input/source)  is missing!")
            error.err_out()

        if (args.insts or args.vars) and not args.stats:
            error = Error(10, "With argument insts/vars must be also arguments stats!")
            error.err_out()

        if not args.stats:
            stats_file = None
        else:
            stats_file = args.stats

        if args.source and args.input:
            return args.source, args.input, stats_file

        if args.source:
            return args.source, None, stats_file
        if args.input:
            return None, args.input, stats_file
