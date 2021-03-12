"""
Name: run_code.py
Main file: interpret.py
Caption:  Start interpreting the code
Author: Magdaléna Ondrušková <xondru16@stud.fit.vutbr.cz>
Date: 29.03.2020
"""
from intlib.variables import *
import re
from operator import itemgetter


class Interpret:
    def __init__(self, frame, input_source, stats):
        self.data_stack = []
        self.code_to_interpret = []
        self.labels = []
        self.calls = []
        self.input_file = input_source
        self.count_initialized_vars_GF = 0
        self.count_initialized_vars = 0
        self.stats_insts = 0
        self.stats_file = stats
        self.file_lines = []
        self.frame = frame

    def control(self):
        """
        Controls interpretation of code.
        """
        length = len(self.code_to_interpret)
        current_instruction = 0
        self.input_source()
        self.code_to_interpret.sort(key=itemgetter(0))
        code_sorted = []
        i = 0
        while len(code_sorted) < len(self.code_to_interpret):
            code_sorted.append([self.code_to_interpret[i][1], self.code_to_interpret[i][2]])
            i += 1
        self.code_to_interpret = code_sorted
        # goes through code and finds all labels
        while current_instruction < length:
            instruction = self.code_to_interpret[current_instruction][0]
            arguments = self.code_to_interpret[current_instruction][1]
            self.find_labels(instruction, arguments, current_instruction)
            current_instruction += 1

        current_instruction = 0
        # goes through code and interpret instructions
        while current_instruction < length:
            instruction = self.code_to_interpret[current_instruction][0]
            arguments = self.code_to_interpret[current_instruction][1]
            current_instruction = self.run(instruction, arguments, current_instruction)
            self.stats_insts += 1
            self.count_initialized_vars_frames()

        if self.stats_file is not None:
            self.write_stats()

    def write_stats(self):
        stats_file = open(self.stats_file, "w")
        for prog_argument in sys.argv:
            if prog_argument == "--insts":
                stats_file.write(str(self.stats_insts))
                stats_file.write("\n")
            if prog_argument == "--vars":
                stats_file.write(str(self.count_initialized_vars))
                stats_file.write("\n")
        stats_file.close()

    def find_labels(self, instruction, arguments, current_instruction):
        if instruction == "LABEL":
            self.opcode_label(arguments, current_instruction)

    def input_source(self):
        if self.input_file is not None:
            files = open(self.input_file, "r")
            self.file_lines = files.read().splitlines()
            files.close()

    def count_initialized_vars_frames(self):
        count_init_vars_LF = 0
        count_init_vars_TF = 0
        count_init_vars_STACK = 0
        if self.frame.local_frame is not None:
            for var in self.frame.local_frame:
                if var.type is not None:
                    count_init_vars_LF += 1
        if self.frame.temporary_frame is not None:
            for var in self.frame.temporary_frame:
                if var.type is not None:
                    count_init_vars_TF += 1

        for frame_stack in self.frame.stack_frame[:-1]:
            for var in frame_stack:
                if var.type is not None:
                    count_init_vars_STACK += 1

        count_sum = count_init_vars_TF + count_init_vars_LF + count_init_vars_STACK + self.count_initialized_vars_GF
        if count_sum > self.count_initialized_vars:
            self.count_initialized_vars = count_sum

    def opcode_label(self, arguments, current_instruction):
        try:
            for lab in self.labels:
                if lab[1] == arguments[0][1]:
                    raise ERRSemantic("Label already exists!")
            self.labels.append([current_instruction, arguments[0][1]])
        except ERRSemantic as msg:
            error = Error(52, msg)
            error.err_out()

    def run(self, instruction, arguments, current_instruction):
        try:
            if instruction == "WRITE":
                self.opcode_write(arguments)
            elif instruction == "DEFVAR":
                self.opcode_defvar(arguments)
            elif instruction == "MOVE":
                self.opcode_move(arguments)
            elif instruction == "CREATEFRAME":
                self.opcode_createframe()
            elif instruction == "PUSHFRAME":
                self.opcode_pushframe()
            elif instruction == "POPFRAME":
                self.opcode_popframe()
            elif instruction == "PUSHS":
                self.opcode_pushs(arguments)
            elif instruction == "POPS":
                self.opcode_pops(arguments)
            elif instruction == "CONCAT":
                self.opcode_concat(arguments)
            elif instruction == "STRLEN":
                self.opcode_strlen(arguments)
            elif instruction == "EXIT":
                self.opcode_exit(arguments)
            elif instruction == "ADD":
                self.opcode_add(arguments)
            elif instruction == "SUB":
                self.opcode_sub(arguments)
            elif instruction == "MUL":
                self.opcode_mul(arguments)
            elif instruction == "IDIV":
                self.opcode_idiv(arguments)
            elif instruction == "DIV":
                self.opcode_div(arguments)
            elif instruction == "LT":
                self.opcode_lt(arguments)
            elif instruction == "GT":
                self.opcode_gt(arguments)
            elif instruction == "EQ":
                self.opcode_eq(arguments)
            elif instruction == "AND":
                self.opcode_and(arguments)
            elif instruction == "OR":
                self.opcode_or(arguments)
            elif instruction == "NOT":
                self.opcode_not(arguments)
            elif instruction == "INT2CHAR":
                self.opcode_int2char(arguments)
            elif instruction == "STRI2INT":
                self.opcode_stri2int(arguments)
            elif instruction == "GETCHAR":
                self.opcode_getchar(arguments)
            elif instruction == "SETCHAR":
                self.opcode_setchar(arguments)
            elif instruction == "DPRINT":
                self.opcode_dprint(arguments)
            elif instruction == "BREAK":
                self.opcode_break()
            elif instruction == "TYPE":
                self.opcode_type(arguments)
            elif instruction == "JUMP":
                current_instruction = self.opcode_jump(arguments)
                self.stats_insts += 1
            elif instruction == "JUMPIFEQ":
                current_instruction = self.opcode_jumpifeq(arguments, current_instruction)
            elif instruction == "JUMPIFNEQ":
                current_instruction = self.opcode_jumpifneq(arguments, current_instruction)
            elif instruction == "READ":
                self.opcode_read(arguments)
            elif instruction == "CALL":
                current_instruction = self.opcode_call(arguments, current_instruction)
                self.stats_insts += 1
            elif instruction == "RETURN":
                current_instruction = self.opcode_return()
            elif instruction == "CLEARS":
                self.opcode_clears()
            elif instruction == "ADDS":
                self.opcode_adds()
            elif instruction == "SUBS":
                self.opcode_subs()
            elif instruction == "MULS":
                self.opcode_muls()
            elif instruction == "IDIVS":
                self.opcode_idivs()
            elif instruction == "DIVS":
                self.opcode_divs()
            elif instruction == "LTS":
                self.opcode_lts()
            elif instruction == "GTS":
                self.opcode_gts()
            elif instruction == "EQS":
                self.opcode_eqs()
            elif instruction == "ANDS":
                self.opcode_ands()
            elif instruction == "ORS":
                self.opcode_ors()
            elif instruction == "NOTS":
                self.opcode_nots()
            elif instruction == "INT2CHARS":
                self.opcode_int2chars()
            elif instruction == "STRI2INTS":
                self.opcode_stri2ints()
            elif instruction == "JUMPIFEQS":
                current_instruction = self.opcode_jumpifeqs(arguments, current_instruction)
            elif instruction == "JUMPIFNEQS":
                current_instruction = self.opcode_jumpifneqs(arguments, current_instruction)
            elif instruction == "INT2FLOAT":
                self.opcode_int2float(arguments)
            elif instruction == "FLOAT2INT":
                self.opcode_float2int(arguments)
            elif instruction == "INT2FLOATS":
                self.opcode_int2floats()
            elif instruction == "FLOAT2INTS":
                self.opcode_float2ints()
            return current_instruction+1
        except ERRSemantic as msg:
            err = Error(52, msg)
            err.err_out()
        except ERROperandType as msg:
            err = Error(53, msg)
            err.err_out()
        except ERRNotExistVar as msg:
            print(self.labels)
            err = Error(54, msg)
            err.err_out()
        except ERRNotExistFrame as msg:
            err = Error(55, msg)
            err.err_out()
        except ERRMissVal as msg:
            err = Error(56, msg)
            err.err_out()
        except ERRValOp as msg:
            err = Error(57, msg)
            err.err_out()
        except ERRString as msg:
            err = Error(58, msg)
            err.err_out()

    def opcode_write(self, arguments):
        if arguments[0][0] == "var":
            var = self.get_var(arguments[0][1], save_to_var=False)
            if var.type == TYPE_NIL:
                text_to_print = ''
            elif var.type == TYPE_FLOAT:
                text_to_print = str(float.hex(var.val))
            else:
                text_to_print = str(var.val)
        elif arguments[0][0] == "int":
            text_to_print = str(arguments[0][1])
        elif arguments[0][0] == "nil":
            text_to_print = ''
        elif arguments[0][0] == "float":
            text_to_print = str(float.hex(arguments[0][1]))
        else:
            text_to_print = arguments[0][1]
        print(text_to_print, end='')

    def opcode_defvar(self, arguments):
        frames, name = re.split('@', arguments[0][1])
        variable = Variable(name)
        if frames == "GF":
            self.frame.add_to_GF(variable)
        elif frames == "LF":
            self.frame.add_to_LF(variable)
        elif frames == "TF":
            self.frame.add_to_TF(variable)

    def opcode_move(self, arguments):
        variable = self.get_var(arguments[0][1], save_to_var=True)
        if arguments[1][0] == "var":
            var = self.get_var(arguments[1][1], save_to_var=False)
            move_type = var.type
            move_val = var.val
        else:
            move_type = self.converts_to_TYPE(arguments[1][0])
            move_val = arguments[1][1]
        variable.type = move_type
        variable.val = move_val

    def opcode_createframe(self):
        self.frame.temporary_frame = []

    def opcode_pushframe(self):
        self.frame.push_frame()

    def opcode_popframe(self):
        self.frame.pop_frame()

    def opcode_pushs(self, arguments):
        if arguments[0][0] == "var":
            var = self.get_var(arguments[0][1], save_to_var=False)
            symb_type = var.type
            symb_val = var.val
        else:
            symb_type = self.converts_to_TYPE(arguments[0][0])
            symb_val = arguments[0][1]
        self.data_stack.append([symb_type, symb_val])

    def opcode_pops(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        if len(self.data_stack) < 1:
            raise ERRMissVal("Data stack is empty - cant pop!")
        else:
            var.type, var.val = self.data_stack.pop()

    def opcode_concat(self, arguments):
        concat_var = self.get_var(arguments[0][1], save_to_var=True)
        symb1 = self.get_operand_string(arguments[1][0], arguments[1][1])
        symb2 = self.get_operand_string(arguments[2][0], arguments[2][1])
        concat_var.val = symb1 + symb2
        concat_var.type = TYPE_STRING

    def opcode_strlen(self, arguments):
        text = self.get_operand_string(arguments[1][0], arguments[1][1])
        var = self.get_var(arguments[0][1], save_to_var=True)
        var.val = int(len(text))
        var.type = TYPE_INT

    def opcode_exit(self, arguments):
        if arguments[0][0] == "var":
            var = self.get_var(arguments[0][1], save_to_var=False)
            number = var.is_int()
        elif arguments[0][0] == "int":
            number = int(arguments[0][1])
        else:
            raise ERROperandType("Opcode EXIT expected int, got {}.".format(arguments[0][1]))

        if number < 0 or number > 49:
            raise ERRValOp("Opcode EXIT expect number between 0 and 49. ")
        self.stats_insts += 1
        if number == 0:
            if self.stats_file is not None:
                self.write_stats()

        sys.exit(number)

    def opcode_add(self, arguments):
        var, operand1, operand2 = self.arithmetic_operation(arguments, "ADD")
        var.val = operand1 + operand2

    def opcode_sub(self, arguments):
        var, operand1, operand2 = self.arithmetic_operation(arguments, "SUB")
        var.val = operand1 - operand2

    def opcode_mul(self, arguments):
        var, operand1, operand2 = self.arithmetic_operation(arguments, "MUL")
        var.val = operand1 * operand2

    def opcode_idiv(self, arguments):
        var, operand1, operand2 = self.arithmetic_operation(arguments, "IDIV")
        if operand2 == 0:
            raise ERRValOp("Division with zero!")
        var.val = operand1 // operand2

    def opcode_div(self, arguments):
        var, operand1, operand2 = self.arithmetic_operation(arguments, "DIV")
        if operand2 == 0.0:
            raise ERRValOp("Division with zero!")
        var.val = operand1 / operand2

    def opcode_lt(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        var.type = TYPE_BOOL
        op1_val, op2_val = self.get_relational_operation(arguments, "lt")
        if op1_val < op2_val:
            var.val = "true"
        else:
            var.val = "false"

    def opcode_gt(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        var.type = TYPE_BOOL
        op1_val, op2_val = self.get_relational_operation(arguments, "gt")
        if op1_val > op2_val:
            var.val = "true"
        else:
            var.val = "false"

    def opcode_eq(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        var.type = TYPE_BOOL
        op1_val, op2_val = self.get_relational_operation(arguments, "eq")
        if op1_val == op2_val:
            var.val = "true"
        else:
            var.val = "false"

    def opcode_and(self, arguments):
        var, operand1, operand2 = self.logical_operation(arguments)
        if operand1 == "False" or operand2 == "False":
            var.val = "false"
        else:
            var.val = "true"

    def opcode_or(self, arguments):
        var, operand1, operand2 = self.logical_operation(arguments)
        if operand1 == "True" or operand2 == "True":
            var.val = "true"
        else:
            var.val = "false"

    def opcode_not(self, arguments):
        var = self.get_var(arguments[0][1], True)
        var.type = TYPE_BOOL
        operand1 = self.get_logic_operands(arguments[1][0], arguments[1][1])
        if operand1 == "True":
            var.val = "false"
        else:
            var.val = "true"

    def opcode_int2char(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        if arguments[1][0] == "var":
            variable = self.get_var(arguments[1][1], save_to_var=False)
            char_number = variable.is_int()
        elif arguments[1][0] == "int":
            char_number = int(arguments[1][1])
        else:
            raise ERROperandType("Expected int, got something else.")
        try:
            var.val = chr(char_number)
            var.type = TYPE_STRING
        except ValueError:
            raise ERRString("Value in symb is not valid in UNICODE.")

    def opcode_stri2int(self, arguments):
        var, text, position = self.conversion_operation(arguments)
        var.val = ord(text[position])
        var.type = TYPE_INT

    def opcode_getchar(self, arguments):
        var, text, position = self.conversion_operation(arguments)
        var.val = text[position]
        var.type = TYPE_STRING

    def opcode_setchar(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=False)
        var.is_string()
        if arguments[1][0] == "var":
            variable = self.get_var(arguments[1][1], save_to_var=False)
            position = variable.is_int()
        elif arguments[1][0] != "int":
            raise ERROperandType("Expected int, not {}".format(str(arguments[1][0])))
        else:
            position = int(arguments[1][1])

        if arguments[2][0] == "var":
            variable = self.get_var(arguments[2][1], save_to_var=False)
            char_to_change_to = variable.is_string()
        elif arguments[2][0] != "string":
            raise ERROperandType("Expected string, not {}".format(str(arguments[1][0])))
        else:
            char_to_change_to = str(arguments[2][1])

        if len(char_to_change_to) < 1 or position < 0 or position > len(var.val) - 1:
            raise ERRString("Empty string, can not change to this char.")

        if len(char_to_change_to) > 1:
            char_to_change_to = char_to_change_to[0]
        text = var.val
        text = text[:position] + char_to_change_to + text[position + 1:]
        var.val = text

    @staticmethod
    def opcode_dprint(arguments):
        print(arguments[0][1], file=sys.stderr)

    def opcode_break(self):
        sys.stderr.write("----- DEBUG INFO -----\n")
        sys.stderr.write("Total instruction in code: %d \n" % len(self.code_to_interpret))
        sys.stderr.write("Total instruction done (so far) %d\n" % self.stats_insts)
        sys.stderr.write("----- FRAMES ------\n")
        sys.stderr.write("GLOBAL FRAME:\n")
        sys.stderr.write("Total variables: %d \n" % len(self.frame.global_frame))
        sys.stderr.write("Variables (by name) in GF:\n")
        for var in self.frame.global_frame:
            sys.stderr.write(" %s \n" % var.name)
        sys.stderr.write("---------------\n")
        sys.stderr.write("LOCAL FRAME:\n")
        if self.frame.local_frame is None:
            sys.stderr.write("Local Frame is not defined.\n")
        else:
            sys.stderr.write("Total variables: %d \n" % len(self.frame.local_frame))
            sys.stderr.write("Variables (by name) in LF:\n")
            for var in self.frame.local_frame:
                sys.stderr.write(" %s \n" % var.name)
        sys.stderr.write("--------------- \n")
        sys.stderr.write("TEMPORARY FRAME:\n")
        if self.frame.temporary_frame is None:
            sys.stderr.write("Temporary Frame is not defined.\n")
        else:
            sys.stderr.write("Total variables: %d\n" % len(self.frame.temporary_frame))
            sys.stderr.write("Variables (by name) in TF:\n")
            for var in self.frame.temporary_frame:
                sys.stderr.write(" %s \n" % var.name)
        sys.stderr.write("----- DEBUG INFO END ------\n")

    def opcode_type(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        if arguments[1][0].lower() != "var":
            symb_type = arguments[1][0].lower()
        else:
            var2 = self.get_var(arguments[1][1], save_to_var=True)
            if var2.type == TYPE_INT:
                symb_type = "int"
            elif var2.type == TYPE_STRING:
                symb_type = "string"
            elif var2.type == TYPE_BOOL:
                symb_type = "bool"
            elif var2.type == TYPE_NIL:
                symb_type = "nil"
            elif var2.type == TYPE_FLOAT:
                symb_type = "float"
            else:
                symb_type = ''

        var.val = symb_type
        var.type = TYPE_STRING

    def opcode_jump(self, arguments):
        label_name = arguments[0][1]
        for lab in self.labels:
            if lab[1] == label_name:
                return lab[0]
        raise ERRSemantic("Label not defined.")

    def opcode_jumpifeq(self, arguments, current_instruction):
        op1_val, op2_val = self.get_relational_operation(arguments, "eq")
        find = False
        position = current_instruction
        for lab in self.labels:
            if lab[1] == arguments[0][1]:
                position = lab[0]
                find = True
        if find is not True:
            raise ERRSemantic("Not existing label.")
        if op1_val == op2_val:
            self.stats_insts += 1
            return position
        else:
            return current_instruction

    def opcode_jumpifneq(self, arguments, current_instruction):
        op1_val, op2_val = self.get_relational_operation(arguments, "eq")
        find = False
        position = current_instruction
        for lab in self.labels:
            if lab[1] == arguments[0][1]:
                position = lab[0]
                find = True
        if find is not True:
            raise ERRSemantic("Not existing label.")
        if op1_val != op2_val:
            self.stats_insts += 1
            return position
        else:
            return current_instruction

    def opcode_read(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        if arguments[1][0] != "type":
            raise ERROperandType("Expected type, got {}".format(arguments[1][0]))
        read_type = arguments[1][1].lower()
        if self.input_file is None:
            try:
                read_value = input()
            except(KeyboardInterrupt, EOFError):
                read_value = None
        else:
            try:
                read_value = self.file_lines.pop(0)
            except IndexError:
                read_value = None

        if read_value is None:
            var.val = "nil"
            var.type = TYPE_NIL
        elif read_type == "bool":
            var.type = TYPE_BOOL
            read_value = str(read_value).lower()
            if read_value.lower() == "true":
                var.val = "true"
            else:
                var.val = "false"
        elif read_type == "int":
            try:
                var.val = int(read_value)
                var.type = TYPE_INT
            except (ValueError, TypeError):
                var.type = TYPE_NIL
                var.val = "nil"
        elif read_type == "string":
            var.type = TYPE_STRING
            var.val = read_value
        elif read_type == "float":
            var.type = TYPE_FLOAT
            try:
                var.val = float.fromhex(read_value)
            except (ValueError, TypeError):
                var.val = float(int(read_value))

    def opcode_call(self, arguments, current_instruction):
        self.calls.append(current_instruction)
        for lab in self.labels:
            if lab[1] == arguments[0][1]:
                return lab[0]
        raise ERRSemantic("Label doesn't exist - can't jump.")

    def opcode_return(self):
        if len(self.calls) < 1:
            raise ERRMissVal("Missing value on stack of calls.")
        else:
            return self.calls.pop()

    def opcode_int2float(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        if arguments[1][0].lower() == "var":
            variable = self.get_var(arguments[1][1], save_to_var=False)
            int_number = variable.is_int()
        elif arguments[1][0].lower() != "int":
            raise ERROperandType("Can not transform type {} to float!".format(arguments[1][0]))
        else:
            int_number = int(arguments[1][1])
        var.type = TYPE_FLOAT
        var.val = float(int_number)

    def opcode_float2int(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        if arguments[1][0].lower() == "var":
            variable = self.get_var(arguments[1][1], save_to_var=False)
            int_number = variable.is_float()
        elif arguments[1][0].lower() != "float":
            raise ERROperandType("Can not transform type {} to int!".format(arguments[1][0]))
        else:
            int_number = float(arguments[1][1])
        var.type = TYPE_INT
        var.val = int(int_number)

#############################
#   ZÁSOBNÍKOVÉ INŠTRUKCIE  #
#############################
    def opcode_clears(self):
        self.data_stack = []

    def opcode_adds(self):
        symb1, symb2, type_symb = self.get_arithmetic_operands_stack("ADDS")
        result = symb1 + symb2
        self.data_stack.append([type_symb, result])

    def opcode_subs(self):
        symb1, symb2, type_symb = self.get_arithmetic_operands_stack("SUBS")
        result = symb1 - symb2
        self.data_stack.append([type_symb, result])

    def opcode_muls(self):
        symb1, symb2, type_symb = self.get_arithmetic_operands_stack("MULS")
        result = symb1 * symb2
        self.data_stack.append([type_symb, result])

    def opcode_idivs(self):
        symb1, symb2, type_symb = self.get_arithmetic_operands_stack("IDIVS")
        if symb2 == 0:
            raise ERRValOp("Division with zero!")
        result = symb1 // symb2
        self.data_stack.append([type, result])

    def opcode_divs(self):
        symb1, symb2, type_symb = self.get_arithmetic_operands_stack("DIVS")
        if symb2 == 0.0:
            raise ERRValOp("Division with zero!")
        result = symb1 / symb2
        self.data_stack.append([type_symb, result])

    def opcode_lts(self):
        symb1, symb2 = self.get_relational_operands_stack("LTS")
        if symb1 < symb2:
            self.data_stack.append([TYPE_BOOL, "true"])
        else:
            self.data_stack.append([TYPE_BOOL, "false"])

    def opcode_gts(self):
        symb1, symb2 = self.get_relational_operands_stack("GTS")
        if symb1 > symb2:
            self.data_stack.append([TYPE_BOOL, "true"])
        else:
            self.data_stack.append([TYPE_BOOL, "false"])

    def opcode_eqs(self):
        symb1, symb2 = self.get_relational_operands_stack("EQS")
        if symb1 == symb2:
            self.data_stack.append([TYPE_BOOL, "true"])
        else:
            self.data_stack.append([TYPE_BOOL, "false"])
        pass

    def opcode_ands(self):
        symb1, symb2 = self.get_logical_operands_stack()
        if symb1 == "False" or symb2 == "False":
            self.data_stack.append([TYPE_BOOL, "false"])
        else:
            self.data_stack.append([TYPE_BOOL, "true"])

    def opcode_ors(self):
        symb1, symb2 = self.get_logical_operands_stack()
        if symb1 == "True" or symb2 == "True":
            self.data_stack.append([TYPE_BOOL, "true"])
        else:
            self.data_stack.append([TYPE_BOOL, "false"])

    def opcode_nots(self):
        if len(self.data_stack) < 1:
            raise ERRMissVal("Missing value on data stack.")
        symb1_type, symb1_val = self.data_stack.pop()
        if symb1_type != TYPE_BOOL:
            raise ERROperandType("Expected bool")
        if symb1_val.capitalize() == "False":
            self.data_stack.append([TYPE_BOOL, "true"])
        else:
            self.data_stack.append([TYPE_BOOL, "false"])

    def opcode_int2chars(self):
        if len(self.data_stack) < 1:
            raise ERRMissVal("Empty data stack.")
        symb1_type, symb1_val = self.data_stack.pop()
        if symb1_type != TYPE_INT:
            raise ERROperandType("Expected integer!")
        try:
            char = chr(int(symb1_val))
            self.data_stack.append([TYPE_STRING, char])
        except ValueError:
            raise ERRString("Not valid ordinal value!")
        pass

    def opcode_stri2ints(self):
        symb1_type, symb1_val, symb2_type, symb2_val = self.get_two_operands_stack()
        if symb2_type != TYPE_INT:
            raise ERROperandType("Expected int.")
        if symb1_type != TYPE_STRING:
            raise ERROperandType("Expected string.")
        if int(symb2_val) > len(symb1_val) - 1:
            raise ERRString("Trying to get on position not in string.")
        text = str(symb1_val)
        number = int(symb2_val)
        self.data_stack.append([TYPE_INT, ord(text[number])])

    def opcode_jumpifeqs(self, arguments, current_instruction):
        symb1_val, symb2_val = self.get_relational_operands_stack("EQS")
        found = False
        position = current_instruction
        for lab in self.labels:
            if lab[1] == arguments[0][1]:
                position = lab[0]
                found = True
        if found is not True:
            raise ERRSemantic("Did not find label!")
        if symb1_val == symb2_val:
            self.stats_insts += 1
            return position
        else:
            return current_instruction

    def opcode_jumpifneqs(self, arguments, current_instruction):
        symb1_val, symb2_val = self.get_relational_operands_stack("EQS")
        found = False
        position = current_instruction
        for lab in self.labels:
            if lab[1] == arguments[0][1]:
                position = lab[0]
                found = True
        if found is not True:
            raise ERRSemantic("Did not find label!")
        if symb1_val != symb2_val:
            self.stats_insts += 1
            return position
        else:
            return current_instruction

    def opcode_int2floats(self):
        if len(self.data_stack) < 1:
            raise ERRMissVal("Missing value on data stack.")
        symb1_type, symb1_val = self.data_stack.pop()
        if symb1_type != TYPE_INT:
            raise ERROperandType("Expected int")
        float_number = float(symb1_val)
        self.data_stack.append([TYPE_FLOAT, float_number])

    def opcode_float2ints(self):
        if len(self.data_stack) < 1:
            raise ERRMissVal("Missing value on data stack.")
        symb1_type, symb1_val = self.data_stack.pop()
        if symb1_type != TYPE_FLOAT:
            raise ERROperandType("Expected float")
        int_number = int(symb1_val)
        self.data_stack.append([TYPE_INT, int_number])

#############################
#     POMOCNÉ FUNKCIE       #
#############################
    def get_var(self, var_name, save_to_var):
        var_frame, var_name = re.split('@', var_name)
        if var_frame == "GF":
            succ, var = self.frame.get_from_GF(var_name)
        elif var_frame == "LF":
            succ, var = self.frame.get_from_LF(var_name)
        elif var_frame == "TF":
            succ, var = self.frame.get_from_TF(var_name)
        else:
            raise ERRNotExistFrame("Not existing frame.")

        if succ is True:
            if save_to_var is True:
                if var_frame == "GF" and var.type is None:
                    self.count_initialized_vars_GF += 1
                return var
            elif var.type is None:
                raise ERRMissVal("Variable defined but without any value.")
            else:
                return var
        else:
            raise ERRNotExistVar("Variable {} doesn't exist in frame {} .".format(var_name, var_frame))

    def get_arithmetic_operands(self, arg_type, name):
        if arg_type == "var":
            var = self.get_var(name, save_to_var=False)
            if var.type == TYPE_FLOAT:
                return TYPE_FLOAT, float(var.val)
            elif var.type == TYPE_INT:
                return TYPE_INT, int(var.val)
            else:
                raise ERROperandType("Cannot work with different type than int/float.")
        elif arg_type == "int":
            return TYPE_INT, int(name)
        elif arg_type == "float":
            return TYPE_FLOAT, float(name)
        else:
            raise ERROperandType("Arithmetic operation need type integer or float.")

    def arithmetic_operation(self, arguments, instruction):
        var = self.get_var(arguments[0][1], save_to_var=True)
        operand1_type, operand1 = self.get_arithmetic_operands(arguments[1][0], arguments[1][1])
        operand2_type, operand2 = self.get_arithmetic_operands(arguments[2][0], arguments[2][1])
        if operand1_type != operand2_type:
            raise ERROperandType("Arithmetic instruction can not work with different types. ")
        if instruction == "IDIV":
            if operand1_type == TYPE_FLOAT or operand2_type == TYPE_FLOAT:
                raise ERROperandType("Instruction IDIV can work only with integer!")
        elif instruction == "DIV":
            if operand1_type == TYPE_INT or operand2_type == TYPE_INT:
                raise ERROperandType("Instruction IDIV can work only with float!")
        var.type = operand1_type
        return var, operand1, operand2

    def get_logic_operands(self, arg_type, arg_name):
        if arg_type == "var":
            var = self.get_var(arg_name, save_to_var=False)
            var.is_bool()
            return var.val.capitalize()
        elif arg_type != "bool":
            raise ERROperandType("Should be type bool.")
        else:
            return arg_name.capitalize()

    def logical_operation(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        var.type = TYPE_BOOL
        operand1 = self.get_logic_operands(arguments[1][0], arguments[1][1])
        operand2 = self.get_logic_operands(arguments[2][0], arguments[2][1])
        return var, operand1, operand2

    def get_relational_operands(self, arg_type, arg_name):
        if arg_type == "var":
            var = self.get_var(arg_name, save_to_var=False)
            arg_name = var.val
            arg_type = var.type
        else:
            arg_type = self.converts_to_TYPE(arg_type)
        return arg_type, arg_name

    def get_relational_operation(self, arguments, operation):
        op1_type, op1_val = self.get_relational_operands(arguments[1][0], arguments[1][1])
        op2_type, op2_val = self.get_relational_operands(arguments[2][0], arguments[2][1])
        if operation == "eq":
            if op1_type == TYPE_NIL or op2_type == TYPE_NIL:
                return op1_val, op2_val
        else:
            if op1_type == TYPE_NIL or op2_type == TYPE_NIL:
                raise ERROperandType("Relational operand LT or GT can work only with int, bool or string.")

        if op1_type != op2_type:
            raise ERROperandType("Relational opcode expects same type of operands.")

        if op1_type == TYPE_STRING:
            op1_val = str(op1_val)
            op2_val = str(op2_val)
        elif op1_type == TYPE_INT:
            op1_val = int(op1_val)
            op2_val = int(op2_val)
        return op1_val, op2_val

    def get_operand_string(self, argument_type, argument_name):
        if argument_type == "var":
            var = self.get_var(argument_name, save_to_var=False)
            string_from_symb = var.is_string()
        elif argument_type == "string":
            if argument_name is None:
                string_from_symb = ''
            else:
                string_from_symb = str(argument_name)
        else:
            raise ERROperandType("Cannot concat not-string text.")
        return string_from_symb

    def conversion_operation(self, arguments):
        var = self.get_var(arguments[0][1], save_to_var=True)
        text = self.get_operand_string(arguments[1][0], arguments[1][1])
        if arguments[2][0] == "var":
            var = self.get_var(arguments[2][1], save_to_var=False)
            position = var.is_int()
        elif arguments[2][0] == "int":
            position = int(arguments[2][1])
        else:
            raise ERROperandType("Expected symbol type of int, got different type.")
        if position < 0 or position > len(text) - 1:
            raise ERRString("Position not in string. ")
        return var, text, position

#  STACK pomocné funkcie #
    def get_two_operands_stack(self):
        if len(self.data_stack) < 2:
            raise ERRMissVal("Missing value on data stack!")
        symb2_type, symb2_val = self.data_stack.pop()
        symb1_type, symb1_val = self.data_stack.pop()
        return symb1_type, symb1_val,  symb2_type, symb2_val

    def get_arithmetic_operands_stack(self, operation):
        symb1_type, symb1_val,  symb2_type, symb2_val = self.get_two_operands_stack()
        if symb1_type != TYPE_INT and symb1_type != TYPE_FLOAT:
            raise ERROperandType("Expected int or float, got something else.")
        if symb2_type != TYPE_INT and symb2_type != TYPE_FLOAT:
            raise ERROperandType("Expected int or float, got something else.")
        if operation == "IDIVS":
            if symb1_type != TYPE_INT or symb2_type != TYPE_INT:
                raise ERROperandType("Instruction IDIVS can work only with int!")
            else:
                symb1_val = int(symb1_val)
                symb2_val = int(symb2_val)
        elif operation == "DIVS":
            if symb1_type != TYPE_FLOAT or symb2_type != TYPE_FLOAT:
                raise ERROperandType("Instruction DIVS can work only with float!")
            else:
                symb1_val = float(symb1_val)
                symb2_val = float(symb2_val)
        if symb1_type != symb2_type:
            raise ERROperandType("Arithmetic instruction can work only with same type!")
        if symb1_type == TYPE_INT:
            symb1_val = int(symb1_val)
            symb2_val = int(symb2_val)
        elif symb2_type == TYPE_FLOAT:
            symb1_val = float(symb1_val)
            symb2_val = float(symb2_val)
        return symb1_val, symb2_val, symb1_type

    def get_logical_operands_stack(self):
        symb1_type, symb1_val, symb2_type, symb2_val = self.get_two_operands_stack()
        if symb1_type != TYPE_BOOL:
            raise ERROperandType("Expected bool.")
        if symb2_type != TYPE_BOOL:
            raise ERROperandType("Expected bool")
        return symb1_val.capitalize(), symb2_val.capitalize()

    def get_relational_operands_stack(self, operation):
        symb1_type, symb1_val, symb2_type, symb2_val = self.get_two_operands_stack()
        if operation == "EQS":
            if symb1_type == TYPE_NIL or symb2_type == TYPE_NIL:
                return symb1_val, symb2_val
        else:
            if symb1_type == TYPE_NIL or symb2_type == TYPE_NIL:
                raise ERROperandType("Operation {} can't work with type NIL.".format(operation))

        if symb1_type != symb2_type:
            raise ERROperandType("Relational operation (besides EQS) can not work with different types.")

        if symb1_type == TYPE_STRING:
            symb1_val = str(symb1_val)
            symb2_val = str(symb2_val)
        elif symb1_type == TYPE_INT:
            symb1_val = int(symb1_val)
            symb2_val = int(symb2_val)
        elif symb1_type == TYPE_FLOAT:
            symb1_val = float(symb1_val)
            symb2_val = float(symb2_val)
        return symb1_val, symb2_val

    @staticmethod
    def converts_to_TYPE(type_of_symb):
        type_of_symb = type_of_symb.lower()
        if type_of_symb == "int":
            return TYPE_INT
        elif type_of_symb == "string":
            return TYPE_STRING
        elif type_of_symb == "bool":
            return TYPE_BOOL
        elif type_of_symb == "nil":
            return TYPE_NIL
        elif type_of_symb == "float":
            return TYPE_FLOAT
