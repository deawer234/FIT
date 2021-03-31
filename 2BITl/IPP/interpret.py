import argparse
import sys
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import operator
import re

ops = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.truediv,  # use operator.div for Python 2
    '%' : operator.mod,
    '^' : operator.xor,
    '==': operator.eq,
    '!=': operator.ne,
    '<': operator.lt,
    '>': operator.gt,
    "and": operator.and_,
    "or": operator.or_,
    "not": operator.not_
}

sourceflag = False
inputflag = False
statsflag = False
for i in range(1, len(sys.argv)):
    if sys.argv[i][0:9] == "--source=":
        sourceflag = True
        sourcepath = sys.argv[i][9:len(sys.argv[i])]
    elif sys.argv[i][0:8] == "--input=":
        inputflag = True
        inputpath = sys.argv[i][8:len(sys.argv[i])]
    elif sys.argv[i][0:8] == "--stats=":
        statsflag = True
        statsfile = open(sys.argv[i][8:len(sys.argv[i])], 'w')
        if sys.argv[i + 1] == None:
            sys.exit(10)
    elif sys.argv[i][0:6] == "--help":
        print("help placeholder")
    else: 
        sys.exit(10)

if not sourceflag and not inputflag:
    sys.exit(90) #no args
elif not sourceflag:
    sourcepath = sys.stdin 

if inputflag:
    inputfile = open(inputpath, "r")

if statsflag:
    insts = 0
    hot = 0
    vars = 0

xmltree = ET.parse(sourcepath)
xmlroot = xmltree.getroot()

labelarray = {}
stack = []
callstack = []
framestack = []
framePushed = False
frameCreated = False
tf = {}
lf = {}
gf = {}
framescounter = 0
jumping = False

def seperate_var(var):
    tmp = var.split('@')
    frame = tmp[0]
    var = tmp[1]
    return frame, var

def is_defined(tocheck):
    frame, varid = seperate_var(tocheck)
    if frame == "GF":
        if gf.get(varid) == None:
            sys.stderr.write('Line ' + str(i + 1) + ': Variable '+ tocheck +' is not defined.\n')
            sys.exit(54) #variable doesnt exist
    if frame == "LF":
        if lf.get(varid) == None:
            sys.stderr.write('Line ' + str(i + 1) + ': Variable '+ tocheck +' is not defined.\n')
            sys.exit(54) #variable doesnt exist
    if frame == "TF":
        if tf.get(varid) == None:
            sys.stderr.write('Line ' + str(i + 1) + ': Variable '+ tocheck +' is not defined.\n')
            sys.exit(54) #variable doesnt exist
    
def write_value(tocheck, value):
    frame, varid = seperate_var(tocheck)
    if frame == "GF":
        gf[varid][1] = str(value)
    if frame == "LF":
        lf[varid][1] = str(value)
    if frame == "TF":
        tf[varid][1] = str(value)

def write_type(tocheck, type):
    frame, varid = seperate_var(tocheck)
    if frame == "GF":
        gf[varid][0] = str(type)
    if frame == "LF":
        lf[varid][0] = str(type)
    if frame == "TF":
        tf[varid][0] = str(type)

def get_value(fromvar):
    frame, varid = seperate_var(fromvar)
    if frame == "GF":
        return gf[varid][1]
    if frame == "LF":
        return lf[varid][1]
    if frame == "TF":
        return tf[varid][1]
    
def get_type(fromvar):
    frame, varid = seperate_var(fromvar)
    if frame == "GF":
        return gf[varid][0]
    if frame == "LF":
        return lf[varid][0]
    if frame == "TF":
        return tf[varid][0]

def symb_rec(symbol):
    if symbol.attrib['type'] == "var":
        is_defined(symbol.text)
        return get_type(symbol.text), get_value(symbol.text)
    elif "int" == symbol.attrib['type'] or "string" == symbol.attrib['type'] or "bool" == symbol.attrib['type'] or "nil" == symbol.attrib['type'] or "float" == symbol.attrib['type']:
        return symbol.attrib['type'], symbol.text

def move_var(to, varfrom):
    is_defined(to.text)
    type, varfrom = symb_rec(varfrom)
    if "int" == type or "string" == type or "bool" == type or "nil" == type or "float" == type:
        if "float" == type:
            write_value(to.text, float.fromhex(varfrom))
        if "string" == type and varfrom == None:
            write_value(to.text, "")
        else:
            write_value(to.text, varfrom)
        write_type(to.text, str(type))   

def operation(instr, op):
    is_defined(instr[0].text)
    var = instr[0]
    type1, symb1 = symb_rec(instr[1])
    type2, symb2 = symb_rec(instr[2])

    if type1 == type2 == "int" or type1 == type2 == "float":
        if op == '/' and (int(symb2.text) == 0 or int(get_value(symb2.text)) == 0):
            sys.exit(57) #division by zero
        if "DIV" == instr.attrib['opcode']:
            write_value(var.text, ops[op](float(symb1), float(symb2)))
            write_type(var.text, "float")
        else:
            write_value(var.text, ops[op](int(symb1), int(symb2)))
            write_type(var.text, type1)

def eq_and_neq(instr, op):
    if jumping:
        label = instr[0]
        if labelarray.get(label.text) == None:
            sys.exit(52) #label doesnt exist
    type1, symb1 = symb_rec(instr[1])
    type2, symb2 = symb_rec(instr[2])
    if type1 == type2:
        if type1 == "int":
            symb1 = int(symb1)
            symb2 = int(symb2)
        if type1 == "float":
            symb1 = float(symb1)
            symb2 = float(symb2)
        if ops[op](symb1, symb2):
            return True
        else:
            return False
    else:
        sys.exit(50)#bad type


def logic_op(instr, op):
    type1, symb1 = symb_rec(instr[1])
    type2, symb2 = symb_rec(instr[2])
    if type1 == type2:
        bool1 = False
        bool2 = False
        if symb1 == "false":
            bool1 = False
        else:
            bool1 = True
        if symb2 == "false":
            bool2 = False
        else:
            bool2 = True
        if ops[op](bool1, bool2):
            return True
        else:
            return False
    else:
        sys.exit(50)#bad type
    return False

def replace(match):
    return int(match.group(1)).to_bytes(1, byteorder="big")

for i in range(len(xmlroot)):
    if "LABEL" == xmlroot[i].attrib['opcode']:
        labelarray[xmlroot[i][0].text] = int(xmlroot[i].attrib['order']) - 1

i = 0
while i < len(xmlroot):
    instr = xmlroot[i]
    if "DEFVAR" == instr.attrib['opcode']:
        if "var" == instr[0].attrib['type']:
            frame = instr[0].text.split('@')
            if frame[0] == "GF":
                gf[instr[0].text[3:]] = ["n", "n"]
            if frame[0] == "LF" and framePushed:
                lf[instr[0].text[3:]] = ["n", "n"]
            elif frame[0] == "LF":
                sys.exit(80) #non existing pushed frame
            if frame[0] == "TF" and frameCreated:
                tf[instr[0].text[3:]] = ["n", "n"]
            elif frame[0] == "TF":
                sys.exit(80) #non existing created frame
        else:
            sys.exit(50)

    elif "WRITE" == instr.attrib['opcode']:
        type = instr[0].attrib['type']
        if "int" == type or "string" == type or "bool" == type or "nil" == type:
            print(instr[0].text, end="")
        elif "var" == instr[0].attrib['type']:
            is_defined(instr[0].text) 
            if get_type(instr[0].text) == "string":
                line = get_value(instr[0].text).encode("utf-8")
                regex = re.compile(rb"\\(\d{1,3})")
                new = regex.sub(replace, line)
                print(new.decode("utf-8"), end="") 
            else:
                print(get_value(instr[0].text), end="") 
        else: 
            sys.exit(50)#bad type
    elif "READ" == instr.attrib['opcode']:
        is_defined(instr[0].text)
        var = instr[0]
        type = instr[1].text
        if not inputflag:
            string = input()
        elif inputflag and os.stat(inputpath).st_size != 0:
            string = inputfile.readline()
        else:
            string = input()
        if string == EOFError:
            write_type(var.text, "nil")
        if type == "int" or type == "string" or type == "bool" or type == "float":
            write_value(var.text, string)
            write_type(var.text, type)
        else:
            sys.exit(50)#bad type

    elif "MOVE" == instr.attrib['opcode']:
        move_var(instr[0], instr[1])
    elif "ADD" == instr.attrib['opcode']:
        operation(instr, "+")
    elif "SUB" == instr.attrib['opcode']:
        operation(instr, "-")
    elif "MUL" == instr.attrib['opcode']:
        operation(instr, "*")
    elif "IDIV" == instr.attrib['opcode']:
        operation(instr, "/")
    # FLOAT rozsireni
    elif "DIV" == instr.attrib['opcode']:
        operation(instr, "/")   
    elif "CALL" == instr.attrib['opcode'] or "JUMP" == instr.attrib['opcode']:
        if "CALL" == instr.attrib['opcode']:
            callstack.append(i)
        if labelarray.get(instr[0].text) != None:
            i = labelarray[instr[0].text]
        else:
            sys.exit(52) #label doesnt exist
    elif "RETURN" == instr.attrib['opcode']:
        i = callstack.pop()
        #i = i
    elif "JUMPIFEQ" == instr.attrib['opcode']:
        jumping = True
        if eq_and_neq(instr, "=="):
            i = labelarray[instr[0].text]
        jumping = False
    elif "JUMPIFNEQ" == instr.attrib['opcode']:
        jumping = True
        if eq_and_neq(instr, "!="):
            i = labelarray[instr[0].text]
        jumping = False
    elif "LABEL" == instr.attrib['opcode']:
        i+=1
        continue

    elif "LT" == instr.attrib['opcode']:
        is_defined(instr[1].text)
        if instr[1].attrib['type'] == "nil" or instr[2].attrib['type'] == "nil":
            sys.exit(53) #nil
        elif instr[1].attrib['type'] == "var":
            if get_type(instr[1].text) == "nil":
                sys.exit(53) #nil
        elif instr[2].attrib['type'] == "var":
            if get_type(instr[2].text) == "nil":
                sys.exit(53) #nil
        write_type(instr[0].text, "bool")
        write_value(instr[0].text, str(eq_and_neq(instr, "<")).lower())

    elif "GT" == instr.attrib['opcode']:
        is_defined(instr[1].text)
        if instr[1].attrib['type'] == "nil" or instr[2].attrib['type'] == "nil":
            sys.exit(53) #nil
        elif instr[1].attrib['type'] == "var":
            if get_type(instr[1].text) == "nil":
                sys.exit(53) #nil
        elif instr[2].attrib['type'] == "var":
            if get_type(instr[2].text) == "nil":
                sys.exit(53) #nil
        write_type(instr[0].text, "bool")
        write_value(instr[0].text, str(eq_and_neq(instr, ">")).lower())

    elif "EQ" == instr.attrib['opcode']:
        is_defined(instr[1].text)
        write_value(instr[0].text, str(eq_and_neq(instr, "==")).lower())
        write_type(instr[0].text, "bool")

    elif "AND" == instr.attrib['opcode']:
        is_defined(instr[1].text)
        if instr[1].attrib['type'] != "bool" or instr[2].attrib['type'] != "bool":
            if get_type(instr[1].text) != "bool" or get_type(instr[2].text) != "bool":
                sys.exit(50) #bad type
        write_value(instr[0].text, str(logic_op(instr, "and")).lower())
        write_type(instr[0].text, "bool")

    elif "OR" == instr.attrib['opcode']:
        is_defined(instr[1].text)
        if instr[1].attrib['type'] != "bool" or instr[2].attrib['type'] != "bool":
            if get_type(instr[1].text) != "bool" or get_type(instr[2].text) != "bool":
                sys.exit(50) #bad type
        write_value(instr[0].text, str(logic_op(instr, "or")).lower())
        write_type(instr[0].text, "bool")

    elif "NOT" == instr.attrib['opcode']:
        is_defined(instr[1].text)
        if instr[1].attrib['type'] != "bool":
            if get_type(instr[1].text) != "bool":
                sys.exit(50) #bad type
        write_value(instr[0].text, str(logic_op(instr, "not")).lower())
        write_type(instr[0].text, "bool")

    elif "STRI2INT" == instr.attrib['opcode']:
        var = instr[0]
        is_defined(var.text)
        typestring, string = symb_rec(instr[1])
        typepos, pos = symb_rec(instr[2])
        if typestring == "string" and typepos == "int":
            if int(pos) > len(string):
                sys.exit(58)#index out of range
            write_value(var.text, ord(string[int(pos)]))
            write_type(var.text, "int")
        else:
            sys.exit(50)#bad type

    elif "INT2CHAR" == instr.attrib['opcode']:
        var = instr[0]
        is_defined(var.text)
        type, intchar = symb_rec(instr[1])
        if type == "int":
            if chr(int(intchar))== ValueError:
                sys.exit(58) #chr error
            write_value(var.text, str(chr(int(intchar))))
            write_type(var.text, "string")
        else:
            sys.exit(50)#bad type
    
    elif "INT2FLOAT" == instr.attrib['opcode']:
        var = instr[0]
        is_defined(var.text)
        type, int = symb_rec(instr[1])
        if type == "int":
            write_value(var.text, str(float(intchar)))
            write_type(var.text, "float")
        else:
            sys.exit(50)#bad type
    
    elif "FLOAT2INT" == instr.attrib['opcode']:
        var = instr[0]
        is_defined(var.text)
        type, float = symb_rec(instr[1])
        if type == "float":
            write_value(var.text, str((int(float))))
            write_type(var.text, "int")
        else:
            sys.exit(50)#bad type


    elif "CONCAT" == instr.attrib['opcode']:
        var = instr[0]
        is_defined(var.text)
        type1, symb1 = symb_rec(instr[1])
        type2, symb2 = symb_rec(instr[2])
        if type1 == type2 == "string":
            write_value(var.text, symb1 + symb2)
            write_type(var.text, type1)
        else:
            sys.exit(50)#bad type

    elif "STRLEN" == instr.attrib['opcode']:
        var = instr[0]
        is_defined(var.text)
        type1, symb1 = symb_rec(instr[1])
        if type1 == "string":

            write_value(var.text, len(str(symb1)))
            write_type(var.text, "int")
        else:
            sys.exit(50)#bad type

    elif "GETCHAR" == instr.attrib['opcode']:
        var = instr[0]
        is_defined(var.text)
        type1, symb1 = symb_rec(instr[1])
        type2, symb2 = symb_rec(instr[2])
        if type1 == "string" and type2 == "int":
            if int(symb2) > len(str(symb1)):
                sys.exit(58)#index out of range
            write_value(var.text, symb1[int(symb2)])
            write_type(var.text, type1)
        else:
            sys.exit(50)#bad type

    elif "SETCHAR" == instr.attrib['opcode']:
        typevar, var = symb_rec(instr[0])
        type1, symb1 = symb_rec(instr[1])
        type2, symb2 = symb_rec(instr[2])
        if typevar == "string" and type1 == "int" and type2 == "string":
            if symb1 > len(var):
                sys.exit(58)#index out of range
            var[symb1] = symb2[0]
            write_value(instr[0].text, var)
        else:
            sys.exit(50)#bad type

    elif "TYPE" == instr.attrib['opcode']:
        var = instr[0]
        symb1 = instr[1]
        is_defined(var.text)
        if symb1.attrib['type'] == "var" and get_type(symb1.text) != "n":
            write_value(var.text, get_type(symb1.text))
        elif symb1.attrib['type'] == "var" and get_type(symb1.text) == "n":
            write_value(var.text, "")
        else:
            write_value(var.text , symb1.attrib['type'])
        write_type(var.text, "string")
    
    elif "PUSHS" == instr.attrib['opcode']:
        type, symb = symb_rec(instr[0])
        stack.append((type, symb))

    elif "POPS" == instr.attrib['opcode']:
        is_defined(instr[0].text)
        if not stack:
            sys.exit(56) #stack empty
        symb, type= stack.pop()
        write_value(instr[0].text, type)
        write_type(instr[0].text, symb)

    elif "EXIT" == instr.attrib['opcode']:
        if instr[0].attrib['type'] == "var":
            if get_type(instr[0].text) != "int":
                sys.exit(50)#bad type
            if int(get_value(instr[0].text)) > 49 and int(get_value(instr[0].text)) < 0:
                sys.exit(57)#exit error
            sys.exit(get_value(int(instr[0].text)))
        else:
            if instr[0].attrib['type'] != "int":
                sys.exit(50)#bad type
            if int(instr[0].text) > 49 and int(instr[0].text) < 0:
                sys.exit(57)#exit error
            sys.exit(int(instr[0].text))
    elif "CREATEFRAME" == instr.attrib['opcode']:
        frameCreated = True
        tf.clear()
    elif "PUSHFRAME" == instr.attrib['opcode']:
        frameCreated = False
        framePushed = True
        framestack.append(tf.copy())
        lf = framestack[-1]
        framescounter += 1 
        tf.clear()
    elif "POPFRAME" == instr.attrib['opcode']:
        tf = framestack[-1].copy()
        if framestack.pop() == IndexError:
            sys.exit(55) #framestack empty
        if framestack:
            lf = framestack[-1]
        framescounter -= 1
        if framescounter == 0:
            framePushed = False
    else:
        sys.exit(20)#bad xml
    i+=1
