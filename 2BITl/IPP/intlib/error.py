"""
Name: error.py
Main file: interpret.py
Caption:  Handles errors in interpret.py
Author: Magdaléna Ondrušková <xondru16@stud.fit.vutbr.cz>
Date: 28.03.2020
"""
import sys


class Error:
    def __init__(self, err_code, msg):
        self.err_code = err_code
        self.msg = msg

    def err_out(self):
        """
        Function prints error code + message on stderr and exit program with error code
        ERROR CODES:
            - ET.ParseError - 31 - if XML is not well-formatted
            - ERRConstruction - 32 - used in instruction.py when checking XML format
            - ERRSemantic  - 52 - Error with semantic control (undefined label, re-definition of variable)
            - ERROperandType - 53 - Wrong operand type (INT instead of STRING and so on)
            - ERRNotExistVar - 54 - Trying to access to not-existing variable while frame exists
            - ERRNotExistFrame - 55 - Frame doesnt exist (loading from empty frame stack)
            - ERRMissVal - 56 - Missing value ( in var, on data stack, on stack of calls)
            - ERRValOp - 57 - Wrong value of operation ( div with 0, wrong return code in instruction EXIT)
            - ERRString - 58 - Error while working with string
        """
        print("Error {} : {}".format(self.err_code, self.msg), file=sys.stderr)
        sys.exit(self.err_code)


# Definition of Exceptions
class ERRConstruction(Exception):
    pass


class ERRSemantic(Exception):
    pass


class ERROperandType(Exception):
    pass


class ERRNotExistVar(Exception):
    pass


class ERRNotExistFrame(Exception):
    pass


class ERRMissVal(Exception):
    pass


class ERRValOp(Exception):
    pass


class ERRString(Exception):
    pass
