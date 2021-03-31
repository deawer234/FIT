#!/usr/bin/env python3.8
# -- coding: utf-8 --

import os
import socket
import sys
import threading
import re

UDP_IP = "localhost"
UDP_PORT = 0
FSP = ""
indexflag = False
filecount = 0

# argv check
if len(sys.argv) != 5:
    sys.exit(10)

# argv check
for i in range(1, len(sys.argv)):
    if sys.argv[i] == "-n":
        tmp = sys.argv[i+1].split(':')
        UDP_IP = tmp[0]
        UDP_PORT = int(tmp[1])
    if sys.argv[i] == "-f":
        FSP = sys.argv[i+1]

def UDP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(30)
    try:
        s.sendto(messageUDP.encode(), adress)
        IP = s.recv(1024)
    except socket.timeout:
        sys.stderr.write("Server timeout\n")
        sys.exit(10)
    if IP == b'ERR Not Found':
        sys.stderr.write("File server doesn't exist\n")
        sys.exit(10)
    if IP == b'ERR Syntax':
        sys.stderr.write("Wrong request or wrong server name\n")
        sys.exit(10)
    if not re.search(r"^OK [0-9.]+:[0-9]+", IP.decode()):
        sys.stderr.write("Wrong name server response\n")
        sys.exit(10)
    return IP

def TCP(writeflag, FSP_file, filecount, index): 
    for i in range(0, filecount):
        data = []
        encoded = bytes()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(30)
        s.connect((TCP_IP, int(TCP_PORT)))
        if indexflag:
            s.send("GET {} FSP/1.0\r\nHostname: {}\r\nAgent: xnemec92\r\n\r\n".format(str(index[i]), FSP_server).encode())
            file = str(index[i])
            if file.count('/'):
                if not os.path.exists(index[i].split('/', file.count('/'))[0]):
                    os.mkdir(index[i].split('/', file.count('/'))[0])
        else:
            s.send("GET {} FSP/1.0\r\nHostname: {}\r\nAgent: xnemec92\r\n\r\n".format(FSP_file, FSP_server).encode())
            file = FSP_file
        while True:
            try:
                datacheck = s.recv(128)
                if not datacheck:
                    break
                else:
                    encoded += datacheck
            except socket.timeout:
                sys.stderr.write("Connection timeout\n")
                sys.exit(10)
        s.close()
        stringData = re.search(b'\r\n\r\n', encoded)
        _, head = stringData.span()
        data.append(encoded[head:])
        if not re.search(rb"FSP/1.0 (Success|Bad Request|Not Found|Server Error)\r\nLength:[0-9]+\r\n\r\n$", encoded[:head]):
            sys.stderr.write("Wrong file server response\n")
            sys.exit(10)
        if writeflag:
            f = open(file, "wb")
            for i in range(len(data)):
                f.write(data[i])
            f.close()
            data.clear()
        else:
            return data

FSP_server = FSP[6:].split('/', 1)[0]

if FSP[:3] != "fsp":
    sys.stderr.write("This script only works on fps protocol.\n")
    sys.exit(5)
if re.search(r"[^a-zA-Z0-9-_./]", FSP_server):
    sys.stderr.write("Wrong characters in server name\n")
    sys.exit(5)


FSP_file= FSP[6:].split('/', 1)[1]
adress = (UDP_IP, UDP_PORT)

messageUDP = "WHEREIS {}".format(FSP[6:].split('/', 1)[0])

#UDP nameserver communication
IP = UDP()
TCP_IP = str(IP[3:]).split(':')[0]
TCP_PORT = str(IP[3:]).split(':')[1]
TCP_IP = TCP_IP[2:]
TCP_PORT = TCP_PORT.split('\'')[0]


filecount = 1
if FSP_file == "*":
    index = TCP(False, "index", filecount, None)
    
    if index:
        index = index[0].decode().split("index\r\n")
        index.sort(reverse=True)
        index = index[0].split("\r\n")
        index.remove("")
        filecount = len(index)
        indexflag = True
    TCP(True, None, filecount, index)
else:
    TCP(True, FSP_file, filecount, None)





    





