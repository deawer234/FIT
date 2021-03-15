import argparse
import sys
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import operator

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

for i in range(1, len(sys.argv)):
    if sys.argv[i][0:9] == "--source=":
        sourcepath = sys.argv[i][9:len(sys.argv[i])]
    elif sys.argv[i][0:8] == "--input=":
        inpath = sys.argv[i][8:len(sys.argv[i])]
    elif sys.argv[i][0:6] == "--help":
        print("help placeholder")
    else: 
        sys.exit(10)

xmltree = ET.parse(sourcepath)
xmlroot = xmltree.getroot()

frame = []
tmpvars = []
localvars = []
vars = {}
numvars = {}
stringvars = {}
boolvars = {}
counter = 0
labelarray = {}
stack = []
callstack = []
framestack = []


def type_parse(instr):
    type = vars[instr.text]
    if type == "string":
        return stringvars[instr.text]
    elif type == "int":
        return numvars[instr.text]
    elif type == "bool":   
        return boolvars[instr.text]
    elif type == "nil":
        vars[instr.text] = "nil"
        return vars[instr.text]
    elif type == "n":
        sys.exit(50) #bad type

def move_var(to, varfrom):
    if vars.get(to.text) == None:
        sys.exit(54) #variable doesnt exist
    if "int" == varfrom.attrib['type']:
        numvars[to.text] = varfrom.text
        vars[to.text] = "int"
    elif "string" == varfrom.attrib['type']:
        stringvars[to.text] = varfrom.text
        vars[to.text] = "string"
    elif "bool" == varfrom.attrib['type']:
        boolvars[to.text] = varfrom.text
        vars[to.text] = "bool"
    elif "var" == varfrom.attrib['type']:
        if vars.get(varfrom.text) == None:
            sys.exit(54) #variable doesnt exist
        if "int" == vars[varfrom.text]:
            numvars[to.text] = numvars[varfrom.text]
            vars[to.text] = "int"
        elif "string" == varfrom.attrib['type']:
            stringvars[to.text] =  stringvars[varfrom.text]
            vars[to.text] = "string"
        elif "bool" == varfrom.attrib['type']:
            boolvars[to.text] = boolvars[varfrom.text]
            vars[to.text] = "bool"
        elif None == vars[varfrom.text]:
            sys.exit(50)#bad type

def operation(instr, op):
    var = instr[0]
    symb1 = instr[1]
    symb2 = instr[2]
    type = symb1.attrib['type']
    if symb1.attrib['type'] == "var":
        type = vars[symb1.text]
    if "IDIV" == instr.attrib['opcode']:
        type = "int"
    if "DIV" == instr.attrib['opcode']:
        type = "float"
    if op == '/' and (symb2.text == "0" or numvars[symb2.text] == "0"):
        sys.exit(57) #division by zero
    if vars.get(var.text) == None:
        sys.exit(54) #variable doesnt exist
    elif type == symb1.attrib['type']:
        if type == symb2.attrib['type']:
            numvars[var.text] = ops[op](int(symb1.text), int(symb2.text))
        elif "var" == symb2.attrib['type'] and type == vars[symb2.text]:
            if vars.get(symb2.text) == None:
                sys.exit(54) #variable doesnt exist
            numvars[var.text] = ops[op](int(symb1.text), int(numvars[symb2.text]))
        else:
            sys.exit(54)#bad type
    elif "var" == symb1.attrib['type'] and type == vars[symb1.text]:
        if vars.get(symb1.text) == None:
                sys.exit(54) #variable doesnt exist
        if "var" == symb2.attrib['type'] and type == vars[symb2.text]:
            if vars.get(symb2.text) == None:
                sys.exit(54) #variable doesnt exist
            numvars[var.text] = ops[op](int(numvars[symb1.text]), int(numvars[symb2.text]))
        elif type == symb2.attrib['type']:
            numvars[var.text] = ops[op](int(numvars[symb1.text]), int(symb2.text))
        else:
            sys.exit(54)#bad type
    else:
        sys.exit(50)#bad type
    vars[var.text] = type
    return

def eq_and_neq(instr, op):
        label = instr[0]
        if labelarray.get(label.text) == None:
            sys.exit(52) #label doesnt exist
        symb1 = instr[1]
        symb2 = instr[2]
        if symb1.attrib['type'] == symb2.attrib['type'] and symb1.attrib['type'] != "var":
            if ops[op](str(symb1.text), str(symb2.text)):
            #    return labelarray[label.text]
                return True
        elif symb1.attrib['type'] == vars[symb2.text]:
            if vars.get(symb2.text) == None:
                sys.exit(54) #variable doesnt exist
            symb2 = type_parse(symb2)
            if ops[op](str(symb1.text), str(symb2)):
           #     return labelarray[label.text]
                return True
        elif symb2.attrib['type'] == vars[symb1.text]:
            if vars.get(symb1.text) == None:
                sys.exit(54) #variable doesnt exist
            symb1 = type_parse(symb1)
            if ops[op](str(symb1), str(symb2.text)):
                return True
          #      return labelarray[label.text]
        elif vars[symb1.text] == vars[symb2.text]:
            if vars.get(symb2.text) == None or vars.get(symb1.text) == None:
                sys.exit(54) #variable doesnt exist
            symb1 = type_parse(symb1)
            symb2 = type_parse(symb2)
            if ops[op](str(symb1), str(symb2)):
                return True
         #       return labelarray[label.text]
        #return i
        return False

for i in range(len(xmlroot)):
    if "LABEL" == xmlroot[i].attrib['opcode']:
        labelarray[xmlroot[i][0].text] = int(xmlroot[i].attrib['order']) - 1

i = 0
while i < len(xmlroot):
    instr = xmlroot[i]
    if "DEFVAR" == instr.attrib['opcode']:
        if "var" == instr[0].attrib['type']:
            if "GF" in instr[0].text:
                vars[instr[0].text] = "n"
        else:
            sys.exit(50)

    elif "WRITE" == instr.attrib['opcode']:
        type = instr[0].attrib['type']
        if "int" == type or "string" == type or "bool" == type or "nil" == type:
            print(instr[0].text)
        elif "var" == instr[0].attrib['type']:
            if vars.get(instr[0].text) != None:
                print(type_parse(instr[0]))
            else:  
                sys.exit(54) #variable doesnt exist      
        else: 
            sys.exit(50)#bad type
    elif "READ" == instr.attrib['opcode']:
        if vars.get(instr[0].text) == None:
            sys.exit(54) #variable doesnt exist
        var = instr[0]
        type = instr[1].text
        string = input()
        if string == EOFError:
            vars[var.text] = "nil"
        if type == "int":
            numvars[var.text] = int(string)
            vars[var.text] = "int"
        elif type == "string":
            stringvars[var.text] = string
            vars[var.text] = "string"
        elif type == "bool":
            boolvars[var.text] = bool(string)
            vars[var.text] = "bool"
        else:
            sys.exit(50)#bad type

    elif "MOVE" == instr.attrib['opcode']:
        if vars.get(instr[0].text) == None:
            sys.exit(54) #variable doesnt exist
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
            callstack.append[i]
        if labelarray.get(instr[0].text) != None:
            i = labelarray[instr[0].text]
        else:
            sys.exit(52) #label doesnt exist
    elif "RETURN" == instr.attrib['opcode']:
        i = callstack.pop()
    elif "JUMPIFEQ" == instr.attrib['opcode']:
        if eq_and_neq(instr, "=="):
            i = labelarray[instr[0].text]
    elif "JUMPIFNEQ" == instr.attrib['opcode']:
        if eq_and_neq(instr, "!="):
            i = labelarray[instr[0].text]
    elif "LABEL" == instr.attrib['opcode']:
        i+=1
        continue
    elif "LT" == instr.attrib['opcode']:
        if instr[1].attrib['type'] == "nil" or instr[2].attrib['type'] == "nil":
            sys.exit(53) #nil
        elif vars[instr[1].text] == "nil" or vars[instr[2].text] == "nil":
            sys.exit(53) #nil
        boolvars[instr[0].text] = str(eq_and_neq(instr, "<"))
        vars[instr[0].text] = "bool"
    elif "GT" == instr.attrib['opcode']:
        if instr[1].attrib['type'] == "nil" or instr[2].attrib['type'] == "nil":
            sys.exit(53) #nil
        elif vars[instr[1].text] == "nil" or vars[instr[2].text] == "nil":
            sys.exit(53) #nil
        boolvars[instr[0].text] = str(eq_and_neq(instr, ">"))
        vars[instr[0].text] = "bool"
    elif "EQ" == instr.attrib['opcode']:
        boolvars[instr[0].text] = str(eq_and_neq(instr, "=="))
        vars[instr[0].text] = "bool"
    elif "AND" == instr.attrib['opcode']:
        if instr[1].attrib['type'] != "bool" or instr[2].attrib['type'] != "bool" or vars[instr[1].text] != "bool" or vars[instr[2].text] != "bool":
            sys.exit(50) #bad type
        boolvars[instr[0].text] = str(eq_and_neq(instr, "and"))
        vars[instr[0].text] = "bool"
    elif "OR" == instr.attrib['opcode']:
        if instr[1].attrib['type'] != "bool" or instr[2].attrib['type'] != "bool" or vars[instr[1].text] != "bool" or vars[instr[2].text] != "bool":
            sys.exit(50) #bad type
        boolvars[instr[0].text] = str(eq_and_neq(instr, "or"))
        vars[instr[0].text] = "bool"
    elif "NOT" == instr.attrib['opcode']:
        if instr[1].attrib['type'] != "bool" or vars[instr[1].text] != "bool":
            sys.exit(50) #bad type
        boolvars[instr[0].text] = str(eq_and_neq(instr, "not"))
        vars[instr[0].text] = "bool"
    elif "STR2INT" == instr.attrib['opcode']:
        if vars.get(instr[0].text) == None:
            sys.exit(54) #variable doesnt exist
        var = instr[0]
        string = instr[1]
        pos = instr[2]
        if string.attrib['type'] != "string" or vars[string.text] != "string":
            sys.exit(50)#bad type
        if pos.attrib['type'] != "int" or vars[pos.text] != "int":
            sys.exit(50)#bad type
        if stringvars.get(string.text) != None:
            if vars.get(string.text) == None:
                sys.exit(54) #variable doesnt exist
            if numvars.get(pos.text) != None:
                if vars.get(pos.text) == None:
                    sys.exit(54) #variable doesnt exist
                numvars[var.text] = ord(stringvars[string.text][numvars[pos.text]])
            else:
                numvars[var.text] = ord(stringvars[string.text][pos])
        else:
            numvars[var.text] = ord(string.text[pos])
        vars[var.text] = "string"

    elif "INT2CHAR" == instr.attrib['opcode']:
        if vars.get(instr[0].text) == None:
            sys.exit(54) #variable doesnt exist
        var = instr[0]
        intchar = instr[1]
        if intchar.attrib['type'] != "int" or vars[intchar.text] != "int":
            sys.exit(50)#bad type
        if numvars.get(intchar.text) != None:
            if vars.get(intchar.text) == None:
                sys.exit(54) #variable doesnt exist
            if chr(int(numvars[intchar.text])) != ValueError:
                stringvars[var.text] = chr(int(numvars[intchar.text]))
            else:
                sys.exit(58) #chr error
        else:
            if chr(int(intchar.text)) != ValueError:
                stringvars[var.text] = chr(int(intchar.text))
            else:
                sys.exit(58) #chr error
        vars[var.text] = "int"
    elif "TYPE" == instr.attrib['opcode']:
        var = instr[0]
        symb1 = instr[1]
        if vars.get(symb1.text) != None:
            stringvars[var.text] = vars[symb1.text]
        elif vars.get(symb1.text) != "n":
            stringvars[var.text] = ""
        else:
            stringvars[var.text] = symb1.attrib['type']
        vars[var.text] = "string"
    
    elif "PUSHS" == instr.attrib['opcode']:
        if instr[0].attrib['type'] != var:
            stack.append[instr[0].text]
        else:
            if vars.get(instr[0].text) == None:
                sys.exit(54) #variable doesnt exist
            else:
                stack.append(type_parse(instr))
    elif "POPS" == instr.attrib['opcode']:
        if vars.get(instr[0].text) == None:
            sys.exit(54) #variable doesnt exist
        if stack.count() == 0:
            sys.exit(56) #stack empty
        move_var(instr[0], stack.pop())
        
    elif "EXIT" == instr.attrib['opcode']:
        if instr[0].attrib['type'] != "int" or vars[instr[0].text] != "int":
            sys.exit(50)#bad type
        if numvars.get(instr[0].text) != None:
            if int(numvars[instr[0].text]) > 49 and int(numvars[instr[0].text]) < 0:
                sys.exit(57)#exit error
            sys.exit(numvars[instr[0].text])
        else:
            if int(instr[0].text) > 49 and int(instr[0].text) < 0:
                sys.exit(57)#exit error
            sys.exit(instr[0].text)
    elif "CREATEFRAME" == instr.attrib['opcode']:
        frame = vars                                                                    #TODO
    elif "PUSHFRAME" == instr.attrib['opcode']:
        framestack.append()
    elif "POPFRAME" == instr.attrib['opcode']:
        frame = vars
    else:
        sys.exit(20)#bad xml
    i+=1


